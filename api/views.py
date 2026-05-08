from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import ListAPIView, GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView

from clientes.models import Cliente
from rutas.models import Ruta
from envios.models import Encomienda, HistorialEstado
from config.choices import EstadoEncomienda, EstadoGeneral
from .serializers import (
    ClienteSerializer,
    CustomTokenObtainPairSerializer,
    EncomiendaSerializer,
    EncomiendaDetailSerializer,
    EncomiendaV2Serializer,
    HistorialEstadoSerializer,
    RutaSerializer,
)
from .filters import EncomiendaFilter
from .pagination import EncomiendaPagination, ClientePagination, HistorialPagination
from .permissions import EsEmpleadoActivo, EsPropietarioOAdmin, get_user_empleado


@extend_schema_view(
    list=extend_schema(tags=['Encomiendas']),
    retrieve=extend_schema(tags=['Encomiendas']),
    create=extend_schema(tags=['Encomiendas']),
    update=extend_schema(tags=['Encomiendas']),
    partial_update=extend_schema(tags=['Encomiendas']),
    destroy=extend_schema(tags=['Encomiendas']),
    cambiar_estado=extend_schema(
        request=None,
        responses=EncomiendaDetailSerializer,
        tags=['Encomiendas'],
        description='Cambiar el estado de una encomienda y registrar la transición.',
    ),
    con_retraso=extend_schema(tags=['Encomiendas'], description='Listar encomiendas con retraso.'),
    pendientes=extend_schema(tags=['Encomiendas'], description='Listar encomiendas pendientes.'),
    historial=extend_schema(tags=['Encomiendas'], description='Obtener el historial de estados de una encomienda.'),
    estadisticas=extend_schema(tags=['Encomiendas'], description='Obtener estadísticas de encomiendas.'),
)
class EncomiendaViewSet(ModelViewSet):
    queryset = Encomienda.objects.all()
    serializer_class = EncomiendaSerializer
    pagination_class = EncomiendaPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EncomiendaFilter
    search_fields = ['codigo', 'remitente__apellidos', 'destinatario__apellidos', 'descripcion']
    ordering_fields = ['fecha_envio', 'peso', 'codigo']
    ordering = ['-fecha_envio']

    def get_queryset(self):
        queryset = Encomienda.objects.all()
        if hasattr(queryset, 'con_relaciones'):
            return queryset.con_relaciones()
        return queryset.select_related('remitente', 'destinatario', 'ruta')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EncomiendaDetailSerializer
        return EncomiendaSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [EsEmpleadoActivo(), EsPropietarioOAdmin()]
        return [EsEmpleadoActivo()]

    def perform_create(self, serializer):
        empleado = get_user_empleado(self.request.user)
        if empleado and hasattr(Encomienda, 'empleado_registro'):
            serializer.save(empleado_registro=empleado)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        encomienda = self.get_object()
        estado = request.data.get('estado')
        observacion = request.data.get('observacion')

        if not estado:
            raise ValidationError({'estado': 'El campo estado es requerido.'})

        if estado not in EstadoEncomienda.values:
            raise ValidationError({'estado': 'Estado inválido.'})

        try:
            encomienda.cambiar_estado(estado)
        except Exception as exc:
            raise ValidationError({'detail': str(exc)})

        serializer = self.get_serializer(encomienda)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bulk_estado(self, request):
        ids = request.data.get('ids', [])
        estado = request.data.get('estado')
        if not isinstance(ids, list) or not ids:
            raise ValidationError({'ids': 'Se requiere una lista de ids.'})
        if not estado:
            raise ValidationError({'estado': 'Se requiere un estado.'})

        if estado not in EstadoEncomienda.values:
            raise ValidationError({'estado': 'Estado inválido.'})

        encomiendas = self.get_queryset().filter(id__in=ids)
        if not encomiendas.exists():
            raise ValidationError({'ids': 'No se encontraron encomiendas para esos ids.'})

        updated = []
        for encomienda in encomiendas:
            try:
                encomienda.cambiar_estado(estado)
                updated.append(encomienda)
            except Exception as exc:
                raise ValidationError({'detail': str(exc)})

        serializer = self.get_serializer(updated, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def con_retraso(self, request):
        queryset = self.get_queryset()
        if hasattr(queryset, 'con_retraso'):
            queryset = queryset.con_retraso()
        else:
            limite = timezone.now() - timedelta(days=2)
            queryset = queryset.filter(fecha_entrega__isnull=True, fecha_envio__lt=limite)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        queryset = self.get_queryset()
        if hasattr(queryset, 'pendientes'):
            queryset = queryset.pendientes()
        else:
            queryset = queryset.filter(fecha_entrega__isnull=True)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        encomienda = self.get_object()
        historial = HistorialEstado.objects.filter(encomienda=encomienda).order_by('-fecha')
        paginator = HistorialPagination()
        page = paginator.paginate_queryset(historial, request)
        serializer = HistorialEstadoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        queryset = self.get_queryset()
        total_activas = queryset.filter(fecha_entrega__isnull=True).count()
        en_transito = queryset.filter(estado=EstadoEncomienda.EN_TRANSITO).count()
        con_retraso = queryset.con_retraso().count() if hasattr(queryset, 'con_retraso') else queryset.filter(fecha_entrega__isnull=True, fecha_envio__lt=timezone.now() - timedelta(days=2)).count()
        entregadas_hoy = queryset.filter(
            estado=EstadoEncomienda.ENTREGADA,
            fecha_entrega__date=timezone.localdate(),
        ).count()

        return Response({
            'total_activas': total_activas,
            'en_transito': en_transito,
            'con_retraso': con_retraso,
            'entregadas_hoy': entregadas_hoy,
        })


class EncomiendaV2ViewSet(ReadOnlyModelViewSet):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta').all()
    serializer_class = EncomiendaV2Serializer
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, EsEmpleadoActivo])
def fbv_encomienda_list(request):
    if request.method == 'GET':
        queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta').all()
        serializer = EncomiendaSerializer(queryset, many=True)
        return Response(serializer.data)

    serializer = EncomiendaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, EsEmpleadoActivo])
def fbv_encomienda_detail(request, pk):
    try:
        encomienda = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta').get(pk=pk)
    except Encomienda.DoesNotExist:
        return Response({'detail': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EncomiendaDetailSerializer(encomienda)
        return Response(serializer.data)

    if request.method == 'PATCH':
        serializer = EncomiendaSerializer(encomienda, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    encomienda.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class EncomiendaAPIView(APIView):
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]

    def get(self, request):
        queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta').all()
        serializer = EncomiendaSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EncomiendaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EncomiendaAPIViewDetail(APIView):
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]

    def get_object(self, pk):
        return Encomienda.objects.select_related('remitente', 'destinatario', 'ruta').get(pk=pk)

    def get(self, request, pk):
        try:
            encomienda = self.get_object(pk)
        except Encomienda.DoesNotExist:
            return Response({'detail': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EncomiendaDetailSerializer(encomienda)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            encomienda = self.get_object(pk)
        except Encomienda.DoesNotExist:
            return Response({'detail': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EncomiendaSerializer(encomienda, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            encomienda = self.get_object(pk)
        except Encomienda.DoesNotExist:
            return Response({'detail': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        encomienda.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class EncomiendaMixinList(ListModelMixin, CreateModelMixin, GenericAPIView):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta').all()
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class EncomiendaMixinDetail(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericAPIView):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta').all()
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class EncomiendaGenericList(ListCreateAPIView):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta').all()
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]


class EncomiendaGenericDetail(RetrieveUpdateDestroyAPIView):
    queryset = Encomienda.objects.select_related('remitente', 'destinatario', 'ruta').all()
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]


class ClienteListView(ListAPIView):
    queryset = Cliente.objects.filter(estado=EstadoGeneral.ACTIVO)
    serializer_class = ClienteSerializer
    pagination_class = ClientePagination
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]


class RutaListView(ListAPIView):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated, EsEmpleadoActivo]

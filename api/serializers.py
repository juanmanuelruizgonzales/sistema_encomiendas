from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from clientes.models import Cliente
from rutas.models import Ruta
from envios.models import Encomienda, HistorialEstado
from empleados.models import Empleado


class ClienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo_doc',
            'nro_doc',
            'nombres',
            'apellidos',
            'telefono',
            'email',
            'direccion',
            'estado',
            'fecha_registro',
            'nombre_completo',
            'esta_activo',
        ]


class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = ['id', 'origen', 'destino', 'precio', 'fecha_creacion']


class HistorialEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialEstado
        fields = ['id', 'estado', 'fecha']


class EncomiendaSerializer(serializers.ModelSerializer):
    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)

    remitente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        source='remitente',
        write_only=True,
        required=True,
    )
    destinatario_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        source='destinatario',
        write_only=True,
        required=False,
        allow_null=True,
    )
    ruta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ruta.objects.all(),
        source='ruta',
        write_only=True,
        required=True,
    )
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_entregada = serializers.BooleanField(read_only=True)
    tiene_retraso = serializers.BooleanField(read_only=True)
    dias_en_transito = serializers.IntegerField(read_only=True)
    descripcion_corta = serializers.CharField(read_only=True)

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',
            'descripcion',
            'peso',
            'remitente',
            'destinatario',
            'ruta',
            'estado',
            'fecha_envio',
            'fecha_entrega',
            'remitente_id',
            'destinatario_id',
            'ruta_id',
            'esta_entregada',
            'tiene_retraso',
            'dias_en_transito',
            'descripcion_corta',
            'estado_display',
        ]

    def validate_peso(self, value):
        if value <= 0:
            raise serializers.ValidationError('El peso debe ser mayor a 0.')
        return value

    def validate(self, attrs):
        remitente = attrs.get('remitente')
        destinatario = attrs.get('destinatario')
        fecha_entrega = attrs.get('fecha_entrega')

        if remitente and destinatario and remitente == destinatario:
            raise serializers.ValidationError('El remitente y el destinatario no pueden ser la misma persona.')

        if fecha_entrega and fecha_entrega < timezone.now():
            raise serializers.ValidationError({'fecha_entrega': 'La fecha de entrega no puede estar en el pasado.'})

        return attrs


class EncomiendaDetailSerializer(EncomiendaSerializer):
    historial = HistorialEstadoSerializer(many=True, source='historialestado_set', read_only=True)

    class Meta(EncomiendaSerializer.Meta):
        fields = EncomiendaSerializer.Meta.fields + ['historial']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        empleado = getattr(user, 'empleado', None)
        if not empleado:
            empleado = Empleado.objects.filter(dni=user.username).first()

        if empleado:
            token['empleado_id'] = empleado.pk
            if hasattr(empleado, 'dni'):
                token['dni'] = empleado.dni

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['is_staff'] = self.user.is_staff
        data['is_superuser'] = self.user.is_superuser

        empleado = getattr(self.user, 'empleado', None)
        if not empleado:
            empleado = Empleado.objects.filter(dni=self.user.username).first()

        if empleado:
            data['empleado_id'] = empleado.pk
            if hasattr(empleado, 'dni'):
                data['dni'] = empleado.dni

        return data


class EncomiendaV2Serializer(serializers.ModelSerializer):
    remitente_nombre = serializers.CharField(source='remitente.nombre_completo', read_only=True)
    destinatario_nombre = serializers.CharField(source='destinatario.nombre_completo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Encomienda
        fields = ['id', 'codigo', 'estado', 'estado_display', 'remitente_nombre', 'destinatario_nombre']

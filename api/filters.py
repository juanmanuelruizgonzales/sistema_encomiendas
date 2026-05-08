import django_filters
from datetime import timedelta
from django.utils import timezone

from envios.models import Encomienda
from rutas.models import Ruta


class EncomiendaFilter(django_filters.FilterSet):
    estado = django_filters.CharFilter(field_name='estado')
    ruta = django_filters.ModelChoiceFilter(field_name='ruta', queryset=Ruta.objects.all())
    remitente = django_filters.CharFilter(field_name='remitente__nro_doc', lookup_expr='iexact')
    desde = django_filters.DateTimeFilter(field_name='fecha_envio', lookup_expr='gte')
    hasta = django_filters.DateTimeFilter(field_name='fecha_envio', lookup_expr='lte')
    con_retraso = django_filters.BooleanFilter(method='filter_con_retraso')

    class Meta:
        model = Encomienda
        fields = ['estado', 'ruta', 'remitente', 'desde', 'hasta', 'con_retraso']

    def filter_con_retraso(self, queryset, name, value):
        if not value:
            return queryset

        if hasattr(queryset, 'con_retraso'):
            return queryset.con_retraso()

        limite = timezone.now() - timedelta(days=2)
        return queryset.filter(fecha_entrega__isnull=True, fecha_envio__lt=limite)

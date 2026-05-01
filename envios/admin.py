from django.contrib import admin
from django.utils.html import format_html
from .models import Encomienda, HistorialEstado
from config.choices import EstadoEncomienda


class HistorialInline(admin.TabularInline):
    model = HistorialEstado
    extra = 0


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):

    list_display = (
        'codigo',
        'remitente',
        'destinatario',
        'estado_color',
        'fecha_envio'
    )

    search_fields = ('codigo',)
    list_filter = ('estado', 'fecha_envio',)

    inlines = [HistorialInline]

    fieldsets = (
        ('Información General', {
            'fields': (
                'codigo',
                'descripcion',
                'peso'
            )
        }),

        ('Participantes', {
            'fields': (
                'remitente',
                'destinatario'
            )
        }),

        ('Ruta y Fechas', {
            'fields': (
                'ruta',
                'estado',
                'fecha_entrega'
            )
        }),
    )

    def estado_color(self, obj):

        if obj.estado == EstadoEncomienda.ENTREGADA:
            color = 'green'
        elif obj.estado == EstadoEncomienda.EN_TRANSITO:
            color = 'orange'
        elif obj.estado == EstadoEncomienda.RETRASADA:
            color = 'red'
        else:
            color = 'gray'

        return format_html(
            '<span style="color:{};font-weight:bold;">{}</span>',
            color,
            obj.get_estado_display()
        )

    estado_color.short_description = 'Estado'


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ('encomienda', 'estado', 'fecha')
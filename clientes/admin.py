from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = (
        'nro_doc',
        'nombre_completo',
        'email',
        'estado',
        'fecha_registro'
    )

    search_fields = (
        'nro_doc',
        'nombres',
        'apellidos'
    )

    list_filter = (
        'estado',
        'email'
    )

    ordering = (
        'apellidos',
        'nombres'
    )
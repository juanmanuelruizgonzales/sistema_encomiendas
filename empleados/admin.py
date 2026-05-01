from django.contrib import admin
from .models import Empleado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):

    list_display = (
        'dni',
        'nombres',
        'apellidos',
        'cargo'
    )

    search_fields = (
        'dni',
        'nombres',
        'apellidos',
        'cargo'
    )

    ordering = (
        'apellidos',
        'nombres'
    )
from django.db import models

class Empleado(models.Model):
    dni = models.CharField(max_length=8, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.dni} - {self.nombres}"

    class Meta:
        db_table = 'empleados'


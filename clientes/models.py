from django.db import models
from django.core.exceptions import ValidationError
from config.choices import EstadoGeneral, TipoDocumento
from .querysets import ClienteQuerySet


class ClienteManager(models.Manager):

    def get_queryset(self):
        return ClienteQuerySet(self.model, using=self._db)

    def activos(self):
        return self.get_queryset().activos()

    def buscar(self, termino):
        return self.get_queryset().buscar(termino)


class Cliente(models.Model):
    tipo_doc = models.CharField(
        max_length=3,
        choices=TipoDocumento.choices,
        default=TipoDocumento.DNI
    )

    nro_doc = models.CharField(max_length=15, unique=True)

    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)

    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    estado = models.IntegerField(
        choices=EstadoGeneral.choices,
        default=EstadoGeneral.ACTIVO
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)


    objects = ClienteManager()

    # ---------------- VALIDACIONES ----------------
    def clean(self):
        if len(self.nro_doc) < 8:
            raise ValidationError("El número de documento debe tener al menos 8 caracteres")

        if self.telefono and not self.telefono.isdigit():
            raise ValidationError("El teléfono solo debe contener números")

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def esta_activo(self):
        return self.estado == EstadoGeneral.ACTIVO

    @property
    def total_encomiendas_enviadas(self):
        return self.envios_realizados.count()

    def __str__(self):
        return f'{self.nro_doc} - {self.apellidos}, {self.nombres}'


    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellidos', 'nombres']
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone

from .validators import validar_peso_positivo, validar_codigo_encomienda
from .querysets import EncomiendaQuerySet

from clientes.models import Cliente
from rutas.models import Ruta
from config.choices import EstadoEncomienda

class EncomiendaManager(models.Manager):
    def get_queryset(self):
        return EncomiendaQuerySet(self.model, using=self._db)

    def pendientes(self):
        return self.get_queryset().pendientes()

    def activas(self):
        return self.get_queryset().activas()

    def con_retraso(self):
        return self.get_queryset().con_retraso()

    def por_ruta(self, ruta):
        return self.get_queryset().por_ruta(ruta)


class Encomienda(models.Model):
    codigo = models.CharField(
        max_length=20,
        unique=True,
        validators=[validar_codigo_encomienda]
    )

    descripcion = models.TextField()

    peso = models.FloatField(
        validators=[
            validar_peso_positivo,
            MinValueValidator(0.01)
        ]
    )

    remitente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='envios_realizados'
    )

    destinatario = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='envios_recibidos',
        null=True, blank=True
    )

    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)

    estado = models.CharField(
        max_length=20,
        choices=EstadoEncomienda.choices,
        default=EstadoEncomienda.PENDIENTE
    )

    fecha_envio = models.DateTimeField(auto_now_add=True)

    fecha_entrega = models.DateTimeField(
        null=True, blank=True
    )

    objects = EncomiendaManager()


    def clean(self):
        errors = {}

        if self.remitente and self.remitente.estado != 1:
            errors['remitente'] = "El remitente no está activo"

        if self.remitente and self.destinatario:
            if self.remitente == self.destinatario:
                errors['destinatario'] = "No pueden ser la misma persona"

        if self.estado == EstadoEncomienda.ENTREGADA and not self.fecha_entrega:
            errors['estado'] = "La encomienda debe tener fecha de entrega si está entregada"

        if self.fecha_entrega and self.fecha_entrega < timezone.now():
            errors['fecha_entrega'] = "No puede ser en el pasado"

        if errors:
            raise ValidationError(errors)


    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_estado = None

        if not is_new:
            try:
                previous_estado = Encomienda.objects.get(pk=self.pk).estado
            except Encomienda.DoesNotExist:
                previous_estado = None

        self.full_clean()
        super().save(*args, **kwargs)

        if is_new or not HistorialEstado.objects.filter(encomienda=self).exists():
            HistorialEstado.objects.create(
                encomienda=self,
                estado=self.get_estado_display()
            )
        elif previous_estado and previous_estado != self.estado:
            HistorialEstado.objects.create(
                encomienda=self,
                estado=self.get_estado_display()
            )


    @property
    def esta_entregada(self):
        return self.estado == EstadoEncomienda.ENTREGADA

    @property
    def tiene_retraso(self):
        if self.estado == EstadoEncomienda.EN_TRANSITO:
            return (timezone.now() - self.fecha_envio).days > 2
        return False

    @property
    def dias_en_transito(self):
        if not self.fecha_entrega:
            return (timezone.now() - self.fecha_envio).days
        return (self.fecha_entrega - self.fecha_envio).days

    @property
    def descripcion_corta(self):
        return self.descripcion[:20]

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

        if nuevo_estado == EstadoEncomienda.ENTREGADA and not self.fecha_entrega:
            self.fecha_entrega = timezone.now()

        self.save()


    @classmethod
    def crear_con_costo_calculado(cls, codigo, descripcion, peso, remitente, destinatario, ruta):
        costo = peso * ruta.precio

        return cls.objects.create(
            codigo=codigo,
            descripcion=f"{descripcion} (Costo: {costo})",
            peso=peso,
            remitente=remitente,
            destinatario=destinatario,
            ruta=ruta
        )

    def __str__(self):
        return f"{self.codigo} - {self.remitente}"

    class Meta:
        db_table = 'encomiendas'
        verbose_name = 'Encomienda'
        verbose_name_plural = 'Encomiendas'



class HistorialEstado(models.Model):
    encomienda = models.ForeignKey('Encomienda', on_delete=models.CASCADE)
    estado = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.encomienda.codigo} - {self.estado}"

    class Meta:
        db_table = 'historial_estados'
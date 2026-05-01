from django.db import models
from django.utils import timezone
from datetime import timedelta

class EncomiendaQuerySet(models.QuerySet):

    def pendientes(self):
        return self.filter(fecha_entrega__isnull=True)

    def activas(self):
        return self.filter(fecha_entrega__isnull=True)

    def con_retraso(self):
        limite = timezone.now() - timedelta(days=2)
        return self.filter(
            fecha_entrega__isnull=True,
            fecha_envio__lt=limite
        )

    def por_ruta(self, ruta):
        return self.filter(ruta=ruta)
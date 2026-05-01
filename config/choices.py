from django.db import models

class EstadoGeneral(models.IntegerChoices):
    ACTIVO = 1, 'Activo'
    INACTIVO = 0, 'Inactivo'

class TipoDocumento(models.TextChoices):
    DNI = 'DNI', 'DNI'
    RUC = 'RUC', 'RUC'
    PAS = 'PAS', 'Pasaporte'


class EstadoEncomienda(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    EN_TRANSITO = 'en_transito', 'En tránsito'
    ENTREGADA = 'entregada', 'Entregada'
    RETRASADA = 'retrasada', 'Retrasada'
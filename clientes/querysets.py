from django.db import models

class ClienteQuerySet(models.QuerySet):

    def activos(self):
        return self.filter(estado=1)

    def buscar(self, termino):
        return self.filter(
            models.Q(nombres__icontains=termino) |
            models.Q(apellidos__icontains=termino) |
            models.Q(nro_doc__icontains=termino)
        )
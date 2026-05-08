from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EncomiendaV2ViewSet

router = DefaultRouter()
router.register('encomiendas', EncomiendaV2ViewSet, basename='encomienda-v2')

urlpatterns = [
    path('', include(router.urls)),
]

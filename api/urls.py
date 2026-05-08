from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    EncomiendaViewSet,
    ClienteListView,
    RutaListView,
    EncomiendaAPIView,
    EncomiendaAPIViewDetail,
    EncomiendaMixinList,
    EncomiendaMixinDetail,
    EncomiendaGenericList,
    EncomiendaGenericDetail,
    fbv_encomienda_list,
    fbv_encomienda_detail,
)

router = DefaultRouter()
router.register('encomiendas', EncomiendaViewSet, basename='encomienda')

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('clientes/', ClienteListView.as_view(), name='cliente-list'),
    path('rutas/', RutaListView.as_view(), name='ruta-list'),
    path('fbv/encomiendas/', fbv_encomienda_list, name='fbv-encomienda-list'),
    path('fbv/encomiendas/<int:pk>/', fbv_encomienda_detail, name='fbv-encomienda-detail'),
    path('apiview/encomiendas/', EncomiendaAPIView.as_view(), name='apiview-encomienda-list'),
    path('apiview/encomiendas/<int:pk>/', EncomiendaAPIViewDetail.as_view(), name='apiview-encomienda-detail'),
    path('mixins/encomiendas/', EncomiendaMixinList.as_view(), name='mixins-encomienda-list'),
    path('mixins/encomiendas/<int:pk>/', EncomiendaMixinDetail.as_view(), name='mixins-encomienda-detail'),
    path('generic/encomiendas/', EncomiendaGenericList.as_view(), name='generic-encomienda-list'),
    path('generic/encomiendas/<int:pk>/', EncomiendaGenericDetail.as_view(), name='generic-encomienda-detail'),
    path('', include(router.urls)),
]

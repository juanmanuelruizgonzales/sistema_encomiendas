from django.urls import path
from .views_auth import login_view, logout_view
from .views import (
    dashboard,
    lista_encomiendas,
    detalle_encomienda,
    crear_encomienda,
    perfil,
    cambiar_estado_encomienda
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('lista/', lista_encomiendas, name='lista'),
    path('detalle/<int:pk>/', detalle_encomienda, name='detalle'),
    path('detalle/<int:pk>/cambiar_estado/', cambiar_estado_encomienda, name='cambiar_estado'),
    path('nueva/', crear_encomienda, name='nueva'),
    path('perfil/', perfil, name='perfil'),
]
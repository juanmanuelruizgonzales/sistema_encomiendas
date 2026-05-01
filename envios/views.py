from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages

from .models import Encomienda, HistorialEstado, EstadoEncomienda
from .forms import EncomiendaForm


@login_required
def dashboard(request):

    total = Encomienda.objects.count()

    pendientes = Encomienda.objects.filter(
        estado=EstadoEncomienda.PENDIENTE
    ).count()

    retrasadas = Encomienda.objects.filter(
        estado=EstadoEncomienda.EN_TRANSITO,
        fecha_envio__lt=timezone.now() - timedelta(days=2)
    ).count()

    context = {
        'activas': total,
        'pendientes': pendientes,
        'retrasadas': retrasadas,
    }

    return render(request, 'dashboard.html', context)


@login_required
def lista_encomiendas(request):

    encomiendas = Encomienda.objects.all().order_by('-id')

    estado = request.GET.get('estado')

    if estado == 'pendiente':
        encomiendas = encomiendas.filter(estado=EstadoEncomienda.PENDIENTE)

    elif estado == 'en_transito':
        encomiendas = encomiendas.filter(estado=EstadoEncomienda.EN_TRANSITO)

    elif estado == 'entregada':
        encomiendas = encomiendas.filter(estado=EstadoEncomienda.ENTREGADA)

    elif estado == 'retrasado':
        encomiendas = encomiendas.filter(
            estado=EstadoEncomienda.EN_TRANSITO,
            fecha_envio__lt=timezone.now() - timedelta(days=2)
        )

    paginator = Paginator(encomiendas, 15)
    page = request.GET.get('page')
    encomiendas = paginator.get_page(page)

    return render(request, 'lista.html', {
        'encomiendas': encomiendas
    })

@login_required
def detalle_encomienda(request, pk):

    encomienda = get_object_or_404(Encomienda, pk=pk)

    historial = HistorialEstado.objects.filter(
        encomienda=encomienda
    ).order_by('-fecha')

    return render(request, 'detalle.html', {
        'encomienda': encomienda,
        'historial': historial
    })


@login_required
def cambiar_estado_encomienda(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')

        if nuevo_estado in EstadoEncomienda.values:
            encomienda.cambiar_estado(nuevo_estado)
            messages.success(request, f"Estado cambiado a {encomienda.get_estado_display()}")
        else:
            messages.error(request, 'Estado inválido')

    return redirect('detalle', pk=pk)


@login_required
def crear_encomienda(request):

    if request.method == 'POST':
        form = EncomiendaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Encomienda creada correctamente')
            return redirect('lista')

        else:
            messages.error(request, 'Error al guardar')

    else:
        form = EncomiendaForm()

    return render(request, 'formulario.html', {
        'form': form
    })

@login_required
def perfil(request):
    return render(request, 'perfil.html')
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CitaForm
from .models import Cita


def citas_visibles(usuario):
    citas = Cita.objects.select_related(
        'mascota', 'mascota__propietario', 'veterinario'
    )
    if not usuario.is_staff and usuario.groups.filter(name='Veterinario').exists():
        citas = citas.filter(veterinario__usuario=usuario)
    return citas


def requiere_permiso(request, permiso):
    if not request.user.is_staff and not request.user.has_perm(permiso):
        raise PermissionDenied


@login_required
def lista(request):
    requiere_permiso(request, 'citas.view_cita')

    citas = citas_visibles(request.user).order_by('fecha_hora')
    return render(request, 'citas/lista.html', {'citas': citas})


@login_required
def detalle(request, cita_id):
    requiere_permiso(request, 'citas.view_cita')

    cita = get_object_or_404(
        citas_visibles(request.user),
        cita_id=cita_id,
    )
    return render(request, 'citas/detalle.html', {'cita': cita})


@login_required
def crear(request):
    requiere_permiso(request, 'citas.add_cita')

    form = CitaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cita = form.save()
        return redirect('citas:detalle', cita_id=cita.cita_id)

    return render(request, 'citas/formulario.html', {'form': form, 'titulo': 'Agendar cita'})


@login_required
def editar(request, cita_id):
    requiere_permiso(request, 'citas.change_cita')

    cita = get_object_or_404(citas_visibles(request.user), cita_id=cita_id)
    veterinario_usuario = request.user if request.user.groups.filter(name='Veterinario').exists() else None
    form = CitaForm(request.POST or None, instance=cita, veterinario_usuario=veterinario_usuario)
    if request.method == 'POST' and form.is_valid():
        cita = form.save()
        return redirect('citas:detalle', cita_id=cita.cita_id)

    return render(request, 'citas/formulario.html', {'form': form, 'titulo': 'Editar cita'})


@login_required
def eliminar(request, cita_id):
    requiere_permiso(request, 'citas.delete_cita')

    cita = get_object_or_404(citas_visibles(request.user), cita_id=cita_id)
    if request.method == 'POST':
        cita.delete()
        return redirect('citas:lista')

    return render(request, 'citas/confirmar_eliminacion.html', {'cita': cita})

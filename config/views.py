from django.shortcuts import render

from citas.models import Cita
from mascotas.models import Mascota
from veterinarios.models import Veterinario


def inicio(request):
    context = {
        'mascotas_atendidas': Mascota.objects.count(),
        'citas_registradas': Cita.objects.count(),
        'veterinarios': Veterinario.objects.filter(activo=True).order_by('apellidos', 'nombres')[:3],
        'total_veterinarios': Veterinario.objects.filter(activo=True).count(),
    }
    return render(request, 'inicio.html', context)

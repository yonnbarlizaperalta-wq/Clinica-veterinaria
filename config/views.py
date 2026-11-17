import calendar
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.aplicaciones_vacuna.models import AplicacionVacuna
from apps.citas.models import Cita
from apps.historias_clinicas.models import HistoriaClinica
from apps.mascotas.models import Mascota
from apps.propietarios_core.models import Propietario
from apps.veterinarios.models import Veterinario
from .forms import (
    ActualizarCitaForm,
    AplicacionVacunaForm,
    HistoriaClinicaForm,
    NuevaCitaForm,
    NuevaMascotaForm,
    ReprogramarCitaForm,
    RegistroPropietarioForm,
)


def inicio(request):
    veterinarios = Veterinario.objects.filter(activo=True)

    datos = {
        'mascotas_atendidas': Mascota.objects.count(),
        'citas_registradas': Cita.objects.count(),
        'veterinarios': veterinarios.order_by('apellidos', 'nombres')[:3],
        'total_veterinarios': veterinarios.count(),
    }
    return render(request, 'inicio.html', datos)


def ingresar(request):
    if request.user.is_authenticated:
        if es_personal(request.user):
            return redirect('agenda_personal')
        return redirect('mi_cuenta')

    form = AuthenticationForm(request, data=request.POST or None)
    form.fields['username'].label = 'Correo electrónico'
    form.fields['username'].widget.attrs.update({
        'autocomplete': 'username',
        'placeholder': 'tu@correo.com',
    })
    form.fields['password'].widget.attrs.update({
        'autocomplete': 'current-password',
    })

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        if es_personal(request.user):
            return redirect('agenda_personal')
        return redirect('mi_cuenta')

    return render(request, 'portal/ingresar.html', {'form': form})


def registrar(request):
    if request.user.is_authenticated:
        return redirect('mi_cuenta')

    form = RegistroPropietarioForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data

        with transaction.atomic():
            usuario = get_user_model().objects.create_user(
                username=datos['correo'],
                email=datos['correo'],
                password=datos['password'],
                first_name=datos['nombres'],
                last_name=datos['apellidos'],
            )
            propietario = Propietario.objects.create(
                usuario=usuario,
                nombres=datos['nombres'],
                apellidos=datos['apellidos'],
                documento=datos['documento'],
                telefono=datos['telefono'],
                correo=datos['correo'],
                direccion=datos['direccion'],
            )
            mascota = Mascota.objects.create(
                propietario=propietario,
                nombre=datos['mascota_nombre'],
                especie=datos['especie'],
                raza=datos['raza'],
                sexo=datos['sexo'],
                fecha_nacimiento=datos['fecha_nacimiento'],
            )
            HistoriaClinica.objects.create(
                mascota=mascota,
                fecha_apertura=timezone.localdate(),
                observaciones='Historia clínica iniciada al registrar la mascota.',
            )

        login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(
            request,
            f'¡Bienvenido/a! Ya registramos a {mascota.nombre} en tu cuenta.',
        )
        return redirect('mi_cuenta')

    return render(request, 'portal/registrar.html', {'form': form})


def cerrar_sesion(request):
    if request.method == 'POST':
        logout(request)
    return redirect('inicio')


def es_personal(usuario):
    if not usuario.is_authenticated:
        return False

    return (
        usuario.is_staff
        or usuario.is_superuser
        or usuario.groups.filter(name='Recepcionista').exists()
        or usuario.groups.filter(name='Veterinario').exists()
    )


def es_administrador(usuario):
    return usuario.is_authenticated and (usuario.is_staff or usuario.is_superuser)


def pertenece_rol(usuario, rol):
    return usuario.groups.filter(name=rol).exists()


def veterinario_asignado(usuario):
    if es_administrador(usuario):
        return None

    return Veterinario.objects.filter(usuario=usuario, activo=True).first()


def requiere_personal(usuario, rol=None):
    if es_administrador(usuario):
        return

    if rol and pertenece_rol(usuario, rol):
        return

    if rol is None and es_personal(usuario):
        return

    raise PermissionDenied


def propietario_actual(request):
    return Propietario.objects.filter(usuario=request.user).first()


@login_required
def mi_cuenta(request):
    if es_personal(request.user):
        return redirect('agenda_personal')

    propietario = propietario_actual(request)
    if propietario is None:
        raise PermissionDenied(
            'Esta cuenta aún no está vinculada a un perfil de propietario.'
        )

    mascotas = propietario.mascotas.filter(activo=True)
    citas = Cita.objects.filter(
        mascota__propietario=propietario,
    ).select_related('mascota', 'veterinario').order_by('-fecha_hora')[:8]
    vacunas = AplicacionVacuna.objects.filter(
        mascota__propietario=propietario,
    ).select_related('mascota', 'vacuna').order_by('-fecha')[:8]

    datos = {
        'propietario': propietario,
        'mascotas': mascotas,
        'citas': citas,
        'vacunas': vacunas,
        'ahora': timezone.now(),
    }
    return render(request, 'portal/mi_cuenta.html', datos)


@login_required
def nueva_mascota(request):
    propietario = propietario_actual(request)

    if es_personal(request.user):
        return redirect('agenda_personal')
    if propietario is None:
        return redirect('ingresar')

    form = NuevaMascotaForm(request.POST or None, propietario=propietario)

    if request.method == 'POST' and form.is_valid():
        mascota = form.save()
        messages.success(
            request,
            f'La historia de {mascota.nombre} ya está creada en tu cuenta.',
        )
        return redirect('mi_cuenta')

    return render(request, 'portal/nueva_mascota.html', {'form': form})


@login_required
def nueva_cita(request):
    propietario = propietario_actual(request)

    if es_personal(request.user):
        return redirect('agenda_personal')
    if propietario is None:
        return redirect('ingresar')

    form = NuevaCitaForm(request.POST or None, propietario=propietario)

    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        fecha_hora = datetime.combine(datos['fecha'], datos['hora'])
        fecha_hora = timezone.make_aware(fecha_hora)

        if fecha_hora <= timezone.now():
            form.add_error('hora', 'Elige una hora futura.')
        else:
            cita_ocupada = Cita.objects.filter(
                veterinario=datos['veterinario'],
                fecha_hora=fecha_hora,
            ).exclude(estado=Cita.Estado.CANCELADA).exists()

            if cita_ocupada:
                form.add_error(
                    'hora',
                    'Ese horario ya está ocupado con este veterinario. Elige otra hora.',
                )
            else:
                Cita.objects.create(
                    mascota=datos['mascota'],
                    veterinario=datos['veterinario'],
                    fecha_hora=fecha_hora,
                    motivo=datos['motivo'],
                )
                messages.success(
                    request,
                    'Tu cita quedó solicitada. Puedes consultarla en Mi cuenta.',
                )
                return redirect('mi_cuenta')

    return render(request, 'portal/nueva_cita.html', {'form': form})


@login_required
def reprogramar_cita(request, cita_id):
    personal = es_administrador(request.user) or pertenece_rol(request.user, 'Recepcionista')
    propietario = None if personal else propietario_actual(request)

    if propietario is None and not personal:
        raise PermissionDenied

    citas = Cita.objects.filter(estado=Cita.Estado.PROGRAMADA)
    if propietario:
        citas = citas.filter(mascota__propietario=propietario)
    cita = get_object_or_404(citas, cita_id=cita_id)

    if cita.fecha_hora <= timezone.now():
        messages.error(request, 'Solo se pueden reprogramar citas futuras.')
        return redirect('agenda_personal' if personal else 'mi_cuenta')

    fecha_hora_actual = timezone.localtime(cita.fecha_hora)
    form = ReprogramarCitaForm(
        request.POST or None,
        initial={'fecha':fecha_hora_actual.date(),'hora':fecha_hora_actual.time().replace(tzinfo=None)},
    )

    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        nueva_fecha = datetime.combine(datos['fecha'], datos['hora'])
        nueva_fecha = timezone.make_aware(nueva_fecha)

        if nueva_fecha <= timezone.now():
            form.add_error('hora', 'Elige una hora futura.')
        else:
            horario_ocupado = Cita.objects.filter(
                veterinario=cita.veterinario,
                fecha_hora=nueva_fecha,
            ).exclude(
                cita_id=cita.cita_id,
            ).exclude(
                estado=Cita.Estado.CANCELADA,
            ).exists()

            if horario_ocupado:
                form.add_error(
                    'hora',
                    'El veterinario ya tiene una cita en ese horario. Elige otro.',
                )
            else:
                cita.fecha_hora = nueva_fecha
                cita.save(update_fields=['fecha_hora'])
                messages.success(request, 'La cita quedó reprogramada.')
                return redirect('agenda_personal' if personal else 'mi_cuenta')

    datos_pagina = {'form': form, 'cita': cita}
    return render(request, 'portal/reprogramar_cita.html', datos_pagina)


@login_required
def cancelar_cita(request, cita_id):
    personal = es_administrador(request.user) or pertenece_rol(request.user, 'Recepcionista')
    propietario = None if personal else propietario_actual(request)

    if propietario is None and not personal:
        raise PermissionDenied

    citas = Cita.objects.filter(estado=Cita.Estado.PROGRAMADA)
    if propietario:
        citas = citas.filter(mascota__propietario=propietario)
    cita = get_object_or_404(citas, cita_id=cita_id)

    if cita.fecha_hora <= timezone.now():
        messages.error(request, 'Solo se pueden cancelar citas futuras.')
        return redirect('agenda_personal' if personal else 'mi_cuenta')

    if request.method == 'POST':
        cita.estado = Cita.Estado.CANCELADA
        cita.save(update_fields=['estado'])
        messages.success(request, 'La cita quedó cancelada.')
        return redirect('agenda_personal' if personal else 'mi_cuenta')

    return render(request, 'portal/confirmar_cancelacion.html', {'cita': cita})


@login_required
def nueva_cita_personal(request):
    requiere_personal(request.user, 'Recepcionista')
    form = NuevaCitaForm(request.POST or None, personal=True)

    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        fecha_hora = datetime.combine(datos['fecha'], datos['hora'])
        fecha_hora = timezone.make_aware(fecha_hora)

        if fecha_hora <= timezone.now():
            form.add_error('hora', 'Elige una hora futura.')
        else:
            cita_ocupada = Cita.objects.filter(
                veterinario=datos['veterinario'],
                fecha_hora=fecha_hora,
            ).exclude(estado=Cita.Estado.CANCELADA).exists()

            if cita_ocupada:
                form.add_error(
                    'hora',
                    'Ese horario ya está ocupado con este veterinario. Elige otra hora.',
                )
            else:
                Cita.objects.create(
                    mascota=datos['mascota'],
                    veterinario=datos['veterinario'],
                    fecha_hora=fecha_hora,
                    motivo=datos['motivo'],
                )
                messages.success(request, 'La cita quedó agendada.')
                return redirect('agenda_personal')

    datos_pagina = {'form': form, 'personal': True}
    return render(request, 'portal/nueva_cita.html', datos_pagina)


@login_required
def historia_mascota(request, mascota_id):
    mascota = get_object_or_404(
        Mascota.objects.select_related('propietario'),
        mascota_id=mascota_id,
    )

    if es_personal(request.user):
        requiere_personal(request.user, 'Veterinario')
        veterinario = veterinario_asignado(request.user)

        if veterinario and not es_administrador(request.user):
            tiene_cita = Cita.objects.filter(
                mascota=mascota,
                veterinario=veterinario,
            ).exists()
            if not tiene_cita:
                raise PermissionDenied
    elif mascota.propietario.usuario_id != request.user.id:
        raise PermissionDenied

    try:
        historia = mascota.historia_clinica
    except HistoriaClinica.DoesNotExist:
        historia = None

    consultas = Cita.objects.filter(
        mascota=mascota,
        estado=Cita.Estado.ATENDIDA,
    ).select_related('veterinario').order_by('-fecha_hora')
    vacunas = AplicacionVacuna.objects.filter(
        mascota=mascota,
    ).select_related('vacuna', 'veterinario').order_by('-fecha')

    datos = {
        'mascota': mascota,
        'historia': historia,
        'consultas': consultas,
        'vacunas': vacunas,
    }
    return render(request, 'portal/historia.html', datos)


@login_required
def calendario(request):
    propietario = None

    if not es_personal(request.user):
        propietario = propietario_actual(request)
        if propietario is None:
            raise PermissionDenied

    hoy = timezone.localdate()
    try:
        year = int(request.GET.get('year', hoy.year))
        month = int(request.GET.get('month', hoy.month))
        if month < 1 or month > 12 or year < 2000 or year > 2100:
            raise ValueError
    except (TypeError, ValueError):
        year = hoy.year
        month = hoy.month

    inicio_mes = date(year, month, 1)
    primer_dia_mes_siguiente = (inicio_mes.replace(day=28) + timedelta(days=4))
    primer_dia_mes_siguiente = primer_dia_mes_siguiente.replace(day=1)
    ultimo_dia_mes = primer_dia_mes_siguiente - timedelta(days=1)

    citas = Cita.objects.filter(
        fecha_hora__date__gte=inicio_mes,
        fecha_hora__date__lte=ultimo_dia_mes,
    ).exclude(
        estado=Cita.Estado.CANCELADA,
    ).select_related('mascota', 'veterinario').order_by('fecha_hora')

    if propietario:
        citas = citas.filter(mascota__propietario=propietario)
    elif pertenece_rol(request.user, 'Veterinario') and not es_administrador(request.user):
        veterinario = veterinario_asignado(request.user)
        if veterinario:
            citas = citas.filter(veterinario=veterinario)
        else:
            citas = citas.none()

    citas_por_dia = {}
    for cita in citas:
        dia = timezone.localtime(cita.fecha_hora).day
        if dia not in citas_por_dia:
            citas_por_dia[dia] = []
        citas_por_dia[dia].append(cita)

    semanas = []
    calendario_mes = calendar.Calendar(firstweekday=0)
    for semana in calendario_mes.monthdayscalendar(year, month):
        celdas = []
        for dia in semana:
            if dia == 0:
                citas_del_dia = []
                es_hoy = False
            else:
                citas_del_dia = citas_por_dia.get(dia, [])
                es_hoy = date(year, month, dia) == hoy

            celdas.append({
                'day': dia,
                'citas': citas_del_dia,
                'today': es_hoy,
            })
        semanas.append(celdas)

    mes_anterior = inicio_mes - timedelta(days=1)
    nombres_meses = [
        '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
    ]
    dias_semana = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

    datos = {
        'weeks': semanas,
        'weekdays': dias_semana,
        'mes': nombres_meses[month].capitalize(),
        'year': year,
        'prev_month': mes_anterior.month,
        'prev_year': mes_anterior.year,
        'next_month': primer_dia_mes_siguiente.month,
        'next_year': primer_dia_mes_siguiente.year,
        'personal': propietario is None,
        'citas_mes': sum(len(citas_del_dia) for citas_del_dia in citas_por_dia.values()),
    }
    return render(request, 'portal/calendario.html', datos)


@login_required
def agenda_personal(request):
    requiere_personal(request.user)
    hoy = timezone.localdate()

    citas = Cita.objects.filter(
        fecha_hora__date__gte=hoy,
    ).exclude(
        estado=Cita.Estado.CANCELADA,
    ).select_related(
        'mascota', 'mascota__propietario', 'veterinario',
    ).order_by('fecha_hora')

    es_veterinario = pertenece_rol(request.user, 'Veterinario')
    es_admin = es_administrador(request.user)

    if es_veterinario and not es_admin:
        veterinario = veterinario_asignado(request.user)
        if veterinario:
            citas = citas.filter(veterinario=veterinario)
        else:
            citas = citas.none()

    datos = {
        'citas': citas[:60],
        'hoy': hoy,
        'es_admin': es_admin,
        'es_recepcionista': pertenece_rol(request.user, 'Recepcionista') and not es_admin,
        'es_veterinario': es_veterinario and not es_admin,
        'perfil_veterinario': veterinario_asignado(request.user) if es_veterinario and not es_admin else True,
    }
    return render(request, 'portal/agenda_personal.html', datos)


@login_required
def atender_cita(request, cita_id):
    requiere_personal(request.user, 'Veterinario')

    citas = Cita.objects.select_related(
        'mascota', 'veterinario', 'mascota__propietario',
    )
    veterinario = veterinario_asignado(request.user)

    if not es_administrador(request.user):
        if veterinario:
            citas = citas.filter(veterinario=veterinario)
        else:
            citas = citas.none()

    cita = get_object_or_404(citas, cita_id=cita_id)
    historia, _ = HistoriaClinica.objects.get_or_create(
        mascota=cita.mascota,
        defaults={'fecha_apertura': timezone.localdate()},
    )
    form = ActualizarCitaForm(request.POST or None, instance=cita)
    historia_form = HistoriaClinicaForm(
        request.POST or None,
        instance=historia,
        prefix='historia',
    )

    if request.method == 'POST' and form.is_valid() and historia_form.is_valid():
        with transaction.atomic():
            form.save()
            historia_form.save()

        messages.success(request, 'La cita y la nota clínica quedaron actualizadas.')
        return redirect('agenda_personal')

    datos = {
        'form': form,
        'historia_form': historia_form,
        'cita': cita,
    }
    return render(request, 'portal/atender_cita.html', datos)


@login_required
def registrar_vacuna(request):
    requiere_personal(request.user, 'Veterinario')
    veterinario = veterinario_asignado(request.user)

    if not es_administrador(request.user) and veterinario is None:
        messages.error(
            request,
            'Tu cuenta aún no está vinculada a un perfil veterinario. '
            'Pide al administrador que la asigne.',
        )
        return redirect('agenda_personal')

    form = AplicacionVacunaForm(request.POST or None, veterinario=veterinario)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            'La aplicación de vacuna quedó registrada en la historia de la mascota.',
        )
        return redirect('agenda_personal')

    return render(request, 'portal/registrar_vacuna.html', {'form': form})

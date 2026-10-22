import calendar
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from aplicaciones_vacuna.models import AplicacionVacuna
from citas.models import Cita
from .forms import AplicacionVacunaForm, ActualizarCitaForm, HistoriaClinicaForm, NuevaCitaForm, NuevaMascotaForm, RegistroPropietarioForm
from historias_clinicas.models import HistoriaClinica
from mascotas.models import Mascota
from propietarios_core.models import Propietario
from veterinarios.models import Veterinario


def inicio(request):
    context = {
        'mascotas_atendidas': Mascota.objects.count(),
        'citas_registradas': Cita.objects.count(),
        'veterinarios': Veterinario.objects.filter(activo=True).order_by('apellidos', 'nombres')[:3],
        'total_veterinarios': Veterinario.objects.filter(activo=True).count(),
    }
    return render(request, 'inicio.html', context)


def ingresar(request):
    if request.user.is_authenticated:
        return redirect('agenda_personal' if es_personal(request.user) else 'mi_cuenta')
    form = AuthenticationForm(request, data=request.POST or None)
    form.fields['username'].label = 'Correo electrónico'
    form.fields['username'].widget.attrs.update({'autocomplete':'username','placeholder':'tu@correo.com'})
    form.fields['password'].widget.attrs.update({'autocomplete':'current-password'})
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('agenda_personal' if es_personal(request.user) else 'mi_cuenta')
    return render(request, 'portal/ingresar.html', {'form':form})


def registrar(request):
    if request.user.is_authenticated:
        return redirect('mi_cuenta')
    form = RegistroPropietarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        with transaction.atomic():
            user = get_user_model().objects.create_user(username=data['correo'], email=data['correo'], password=data['password'], first_name=data['nombres'], last_name=data['apellidos'])
            propietario = Propietario.objects.create(usuario=user, nombres=data['nombres'], apellidos=data['apellidos'], documento=data['documento'], telefono=data['telefono'], correo=data['correo'], direccion=data['direccion'])
            mascota = Mascota.objects.create(propietario=propietario, nombre=data['mascota_nombre'], especie=data['especie'], raza=data['raza'], sexo=data['sexo'], fecha_nacimiento=data['fecha_nacimiento'])
            HistoriaClinica.objects.create(mascota=mascota, fecha_apertura=timezone.localdate(), observaciones='Historia clínica iniciada al registrar la mascota.')
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f'¡Bienvenido/a! Ya registramos a {mascota.nombre} en tu cuenta.')
        return redirect('mi_cuenta')
    return render(request, 'portal/registrar.html', {'form':form})


def cerrar_sesion(request):
    if request.method == 'POST':
        logout(request)
    return redirect('inicio')


def es_personal(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.groups.filter(name__in=['Recepcionista','Veterinario']).exists())


def es_administrador(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def pertenece_rol(user, *roles):
    return user.is_authenticated and user.groups.filter(name__in=roles).exists()


def veterinario_asignado(user):
    if es_administrador(user):
        return None
    return Veterinario.objects.filter(usuario=user, activo=True).first()


def requiere_personal(user, *roles):
    if not es_administrador(user) and not pertenece_rol(user, *(roles or ('Recepcionista','Veterinario'))):
        raise PermissionDenied


def _propietario_actual(request):
    return Propietario.objects.filter(usuario=request.user).first()


@login_required
def mi_cuenta(request):
    if es_personal(request.user):
        return redirect('agenda_personal')
    propietario = _propietario_actual(request)
    if not propietario:
        raise PermissionDenied('Esta cuenta aún no está vinculada a un perfil de propietario.')
    mascotas = propietario.mascotas.filter(activo=True)
    citas = Cita.objects.filter(mascota__propietario=propietario).select_related('mascota','veterinario').order_by('-fecha_hora')[:8]
    vacunas = AplicacionVacuna.objects.filter(mascota__propietario=propietario).select_related('mascota','vacuna').order_by('-fecha')[:8]
    return render(request, 'portal/mi_cuenta.html', {'propietario':propietario,'mascotas':mascotas,'citas':citas,'vacunas':vacunas})


@login_required
def nueva_mascota(request):
    propietario=_propietario_actual(request)
    if es_personal(request.user) or not propietario:
        return redirect('agenda_personal' if es_personal(request.user) else 'ingresar')
    form=NuevaMascotaForm(request.POST or None,propietario=propietario)
    if request.method=='POST' and form.is_valid():
        mascota=form.save()
        messages.success(request,f'La historia de {mascota.nombre} ya está creada en tu cuenta.')
        return redirect('mi_cuenta')
    return render(request,'portal/nueva_mascota.html',{'form':form})


@login_required
def nueva_cita(request):
    propietario = _propietario_actual(request)
    if es_personal(request.user) or not propietario:
        return redirect('agenda_personal' if es_personal(request.user) else 'ingresar')
    form = NuevaCitaForm(request.POST or None, propietario=propietario)
    if request.method == 'POST' and form.is_valid():
        data=form.cleaned_data
        fecha_hora=timezone.make_aware(datetime.combine(data['fecha'],data['hora']), timezone.get_current_timezone())
        if fecha_hora <= timezone.now():
            form.add_error('hora','Elige una hora futura.')
        elif Cita.objects.filter(veterinario=data['veterinario'],fecha_hora=fecha_hora).exclude(estado=Cita.Estado.CANCELADA).exists():
            form.add_error('hora','Ese horario ya está ocupado con este veterinario. Elige otra hora.')
        else:
            Cita.objects.create(mascota=data['mascota'],veterinario=data['veterinario'],fecha_hora=fecha_hora,motivo=data['motivo'])
            messages.success(request,'Tu cita quedó solicitada. Puedes consultarla en Mi cuenta.')
            return redirect('mi_cuenta')
    return render(request,'portal/nueva_cita.html',{'form':form})


@login_required
def nueva_cita_personal(request):
    requiere_personal(request.user, 'Recepcionista')
    form=NuevaCitaForm(request.POST or None,personal=True)
    if request.method=='POST' and form.is_valid():
        data=form.cleaned_data
        fecha_hora=timezone.make_aware(datetime.combine(data['fecha'],data['hora']),timezone.get_current_timezone())
        if fecha_hora <= timezone.now():
            form.add_error('hora','Elige una hora futura.')
        elif Cita.objects.filter(veterinario=data['veterinario'],fecha_hora=fecha_hora).exclude(estado=Cita.Estado.CANCELADA).exists():
            form.add_error('hora','Ese horario ya está ocupado con este veterinario. Elige otra hora.')
        else:
            Cita.objects.create(mascota=data['mascota'],veterinario=data['veterinario'],fecha_hora=fecha_hora,motivo=data['motivo'])
            messages.success(request,'La cita quedó agendada.')
            return redirect('agenda_personal')
    return render(request,'portal/nueva_cita.html',{'form':form,'personal':True})


@login_required
def historia_mascota(request, mascota_id):
    mascota=get_object_or_404(Mascota.objects.select_related('propietario'),mascota_id=mascota_id)
    if es_personal(request.user):
        requiere_personal(request.user, 'Veterinario')
        vet=veterinario_asignado(request.user)
        if vet and not es_administrador(request.user) and not Cita.objects.filter(mascota=mascota,veterinario=vet).exists():
            raise PermissionDenied
    elif mascota.propietario.usuario_id != request.user.id:
        raise PermissionDenied
    try:
        historia=mascota.historia_clinica
    except HistoriaClinica.DoesNotExist:
        historia=None
    consultas=Cita.objects.filter(mascota=mascota,estado=Cita.Estado.ATENDIDA).select_related('veterinario').order_by('-fecha_hora')
    vacunas=AplicacionVacuna.objects.filter(mascota=mascota).select_related('vacuna','veterinario').order_by('-fecha')
    return render(request,'portal/historia.html',{'mascota':mascota,'historia':historia,'consultas':consultas,'vacunas':vacunas})


@login_required
def calendario(request):
    if es_personal(request.user):
        owner=None
    else:
        owner=_propietario_actual(request)
        if not owner:
            raise PermissionDenied
    today=timezone.localdate()
    try:
        year=int(request.GET.get('year',today.year)); month=int(request.GET.get('month',today.month))
        if not 1 <= month <= 12 or not 2000 <= year <= 2100: raise ValueError
    except (TypeError,ValueError):
        year,month=today.year,today.month
    start=date(year,month,1)
    next_month=(start.replace(day=28)+timedelta(days=4)).replace(day=1)
    end=next_month-timedelta(days=1)
    query=Cita.objects.filter(fecha_hora__date__gte=start,fecha_hora__date__lte=end).exclude(estado=Cita.Estado.CANCELADA).select_related('mascota','veterinario').order_by('fecha_hora')
    if owner:
        query=query.filter(mascota__propietario=owner)
    elif pertenece_rol(request.user, 'Veterinario') and not es_administrador(request.user):
        vet=veterinario_asignado(request.user)
        query=query.filter(veterinario=vet) if vet else query.none()
    by_day={}
    for cita in query:
        day=timezone.localtime(cita.fecha_hora).day
        by_day.setdefault(day,[]).append(cita)
    weeks=[]
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year,month):
        cells=[]
        for day in week:
            cells.append({'day':day,'citas':by_day.get(day,[]) if day else [],'today':bool(day and date(year,month,day)==today)})
        weeks.append(cells)
    prev=(start-timedelta(days=1));
    following=next_month
    month_names=['','enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
    weekdays=['L','M','X','J','V','S','D']
    return render(request,'portal/calendario.html',{'weeks':weeks,'weekdays':weekdays,'mes':month_names[month].capitalize(),'year':year,'prev_month':prev.month,'prev_year':prev.year,'next_month':following.month,'next_year':following.year,'personal':bool(owner is None),'citas_mes':sum(map(len,by_day.values()))})


@login_required
def agenda_personal(request):
    requiere_personal(request.user)
    today=timezone.localdate()
    citas=Cita.objects.filter(fecha_hora__date__gte=today).select_related('mascota','mascota__propietario','veterinario').order_by('fecha_hora')
    if pertenece_rol(request.user,'Veterinario') and not es_administrador(request.user):
        vet=veterinario_asignado(request.user)
        citas=citas.filter(veterinario=vet) if vet else citas.none()
    citas=citas[:60]
    return render(request,'portal/agenda_personal.html',{'citas':citas,'hoy':today,'es_admin':es_administrador(request.user),'es_recepcionista':pertenece_rol(request.user,'Recepcionista') and not es_administrador(request.user),'es_veterinario':pertenece_rol(request.user,'Veterinario') and not es_administrador(request.user),'perfil_veterinario':veterinario_asignado(request.user) if pertenece_rol(request.user,'Veterinario') and not es_administrador(request.user) else True})


@login_required
def atender_cita(request,cita_id):
    requiere_personal(request.user, 'Veterinario')
    citas=Cita.objects.select_related('mascota','veterinario','mascota__propietario')
    vet=veterinario_asignado(request.user)
    if not es_administrador(request.user):
        citas=citas.filter(veterinario=vet) if vet else citas.none()
    cita=get_object_or_404(citas,cita_id=cita_id)
    historia,_=HistoriaClinica.objects.get_or_create(mascota=cita.mascota,defaults={'fecha_apertura':timezone.localdate()})
    form=ActualizarCitaForm(request.POST or None,instance=cita)
    historia_form=HistoriaClinicaForm(request.POST or None,instance=historia,prefix='historia')
    if request.method=='POST' and form.is_valid() and historia_form.is_valid():
        with transaction.atomic():
            form.save()
            historia_form.save()
        messages.success(request,'La cita y la nota clínica quedaron actualizadas.')
        return redirect('agenda_personal')
    return render(request,'portal/atender_cita.html',{'form':form,'historia_form':historia_form,'cita':cita})


@login_required
def registrar_vacuna(request):
    requiere_personal(request.user, 'Veterinario')
    vet=veterinario_asignado(request.user)
    if not es_administrador(request.user) and not vet:
        messages.error(request,'Tu cuenta aún no está vinculada a un perfil veterinario. Pide al administrador que la asigne.')
        return redirect('agenda_personal')
    form=AplicacionVacunaForm(request.POST or None,veterinario=vet)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'La aplicación de vacuna quedó registrada en la historia de la mascota.')
        return redirect('agenda_personal')
    return render(request,'portal/registrar_vacuna.html',{'form':form})

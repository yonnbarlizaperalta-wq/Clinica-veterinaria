import os
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from propietarios_core.models import Propietario
from mascotas.models import Mascota
from historias_clinicas.models import HistoriaClinica
from veterinarios.models import Veterinario
from vacunas.models import Vacuna
from aplicaciones_vacuna.models import AplicacionVacuna

class Command(BaseCommand):
    help = 'Crea datos demo y cuentas del personal, sin citas ficticias.'

    def handle(self, *args, **options):
        props = []
        for i, (name, surname) in enumerate([('Laura','Pérez'),('Carlos','Gómez'),('María','Díaz')], 1):
            p, _ = Propietario.objects.get_or_create(documento=f'DEMO-CC-{i:03}', defaults={'nombres':name,'apellidos':surname,'telefono':f'30055500{i:02}','correo':f'propietario{i}@demo.local','direccion':f'Calle {i} # 10-20'})
            props.append(p)
        pets = []
        for i, (name, species, sex) in enumerate([('Luna','Canino','H'),('Milo','Felino','M'),('Nala','Canino','H')], 1):
            pet, _ = Mascota.objects.get_or_create(nombre=name, propietario=props[i-1], defaults={'especie':species,'raza':'Mestizo','sexo':sex,'fecha_nacimiento':date(2021+i, 3, 10),'peso_kg':5+i})
            pets.append(pet)
            HistoriaClinica.objects.get_or_create(mascota=pet, defaults={'fecha_apertura':date.today(),'alergias':'Ninguna conocida','antecedentes':'Control preventivo','observaciones':'Registro de demostración'})
        vets = []
        for i, (name, surname, specialty) in enumerate([('Ana','Torres','Medicina general'),('Juan','Ruiz','Dermatología'),('Sofía','Mora','Cirugía')], 1):
            vet, _ = Veterinario.objects.get_or_create(documento=f'VET-DEMO-{i:03}', defaults={'nombres':name,'apellidos':surname,'tarjeta_profesional':f'TP-DEMO-{i:03}','telefono':f'31044400{i:02}','correo':f'veterinario{i}@demo.local','especialidad':specialty})
            vets.append(vet)
        vaccines = []
        for name, species in [('Rabia','Canino'),('Triple felina','Felino'),('Parvovirus','Canino')]:
            vaccine, _ = Vacuna.objects.get_or_create(nombre=name, defaults={'especie_objetivo':species,'fabricante':'Laboratorio Demo','intervalo_meses':12,'descripcion':'Vacuna de demostración'})
            vaccines.append(vaccine)
        # No crear citas de ejemplo: el calendario debe reflejar solo citas
        # registradas por el equipo o solicitadas por propietarios.
        for i in range(3):
            AplicacionVacuna.objects.get_or_create(mascota=pets[i], vacuna=vaccines[i], fecha=date.today()-timedelta(days=30+i), defaults={'veterinario':vets[i],'dosis':'1 ml','lote':f'DEMO-LOT-{i+1:03}','proxima_fecha':date.today()+timedelta(days=335),'observaciones':'Aplicación de demostración'})
        user = os.environ.get('DEMO_ADMIN_USER', 'admin')
        password = os.environ.get('DEMO_ADMIN_PASSWORD', 'Huellitas2026!')
        User = get_user_model()
        if not User.objects.filter(username=user).exists():
            User.objects.create_superuser(username=user, email='admin@huellitas.local', password=password)
        demo_owner = props[0]
        client, client_created = User.objects.get_or_create(
            username='propietario1@demo.local',
            defaults={'email':'propietario1@demo.local','first_name':demo_owner.nombres,'last_name':demo_owner.apellidos},
        )
        if client_created:
            client.set_password('Propietario2026!')
            client.save(update_fields=['password'])
        if demo_owner.usuario_id in (None, client.pk):
            demo_owner.usuario = client
            demo_owner.save(update_fields=['usuario'])
        groups = {
            'Recepcionista': {
                'propietarios_core': ('view_propietario','add_propietario','change_propietario'),
                'mascotas': ('view_mascota','add_mascota','change_mascota'),
                'citas': ('view_cita','add_cita','change_cita'),
                'veterinarios': ('view_veterinario',),
            },
            'Veterinario': {
                'mascotas': ('view_mascota',),
                'historias_clinicas': ('view_historiaclinica','add_historiaclinica','change_historiaclinica'),
                'citas': ('view_cita','change_cita'),
                'vacunas': ('view_vacuna',),
                'aplicaciones_vacuna': ('view_aplicacionvacuna','add_aplicacionvacuna','change_aplicacionvacuna'),
            },
        }
        for group_name, app_permissions in groups.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            permissions = Permission.objects.filter(content_type__app_label__in=app_permissions)
            allowed = [codename for codes in app_permissions.values() for codename in codes]
            group.permissions.set(permissions.filter(codename__in=allowed))
        demo_staff = [
            ('recepcionista@demo.local','Recepcion2026!','Clara','Recepción','Recepcionista'),
        ]
        for username, staff_password, first_name, last_name, group_name in demo_staff:
            staff_user, created = User.objects.get_or_create(username=username, defaults={'email':username,'first_name':first_name,'last_name':last_name,'is_staff':False})
            if created:
                staff_user.set_password(staff_password)
                staff_user.save(update_fields=['password'])
            staff_user.groups.add(Group.objects.get(name=group_name))

        demo_vets = [
            ('ana.torres@demo.local','AnaVet2026!','Ana','Torres','VET-DEMO-001'),
            ('juan.ruiz@demo.local','JuanVet2026!','Juan','Ruiz','VET-DEMO-002'),
            ('sofia.mora@demo.local','SofiaVet2026!','Sofía','Mora','VET-DEMO-003'),
        ]
        for username, staff_password, first_name, last_name, document in demo_vets:
            vet = Veterinario.objects.get(documento=document)
            legacy_user = vet.usuario if vet.usuario_id and vet.usuario.username == 'veterinario@demo.local' else None
            if legacy_user and not User.objects.filter(username=username).exclude(pk=legacy_user.pk).exists():
                staff_user = legacy_user
                staff_user.username = username
                staff_user.email = username
                staff_user.first_name = first_name
                staff_user.last_name = last_name
                staff_user.set_password(staff_password)
                staff_user.save()
                created = False
            else:
                staff_user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'email':username,'first_name':first_name,'last_name':last_name,'is_staff':False},
                )
            if created:
                staff_user.set_password(staff_password)
                staff_user.save(update_fields=['password'])
            staff_user.groups.add(Group.objects.get(name='Veterinario'))
            if vet.usuario_id in (None, staff_user.pk):
                vet.usuario = staff_user
                vet.save(update_fields=['usuario'])
        self.stdout.write(self.style.SUCCESS('Datos demo y cuentas por rol listas; no se crearon citas de ejemplo.'))

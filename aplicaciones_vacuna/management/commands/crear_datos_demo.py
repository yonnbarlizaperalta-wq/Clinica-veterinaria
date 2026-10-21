import os
from datetime import date, datetime, time, timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from propietarios_core.models import Propietario
from mascotas.models import Mascota
from historias_clinicas.models import HistoriaClinica
from veterinarios.models import Veterinario
from citas.models import Cita
from vacunas.models import Vacuna
from aplicaciones_vacuna.models import AplicacionVacuna

class Command(BaseCommand):
    help = 'Crea tres registros de demostración por tabla y un superusuario local.'

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
        now = timezone.localtime()
        for i in range(3):
            instant = now + timedelta(days=i+1)
            Cita.objects.get_or_create(mascota=pets[i], veterinario=vets[i], fecha_hora=instant.replace(hour=9+i, minute=0, second=0, microsecond=0), defaults={'motivo':['Control anual','Consulta dermatológica','Valoración general'][i], 'estado':Cita.Estado.PROGRAMADA})
            AplicacionVacuna.objects.get_or_create(mascota=pets[i], vacuna=vaccines[i], fecha=date.today()-timedelta(days=30+i), defaults={'veterinario':vets[i],'dosis':'1 ml','lote':f'DEMO-LOT-{i+1:03}','proxima_fecha':date.today()+timedelta(days=335),'observaciones':'Aplicación de demostración'})
        user = os.environ.get('DEMO_ADMIN_USER', 'admin')
        password = os.environ.get('DEMO_ADMIN_PASSWORD', 'Huellitas2026!')
        User = get_user_model()
        if not User.objects.filter(username=user).exists():
            User.objects.create_superuser(username=user, email='admin@huellitas.local', password=password)
        self.stdout.write(self.style.SUCCESS('Datos demo listos: 3 registros por cada una de las 7 tablas y superusuario disponible.'))

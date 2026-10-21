from django.contrib import admin
from .models import Mascota
from aplicaciones_vacuna.admin import AplicacionVacunaInline
from historias_clinicas.models import HistoriaClinica

class HistoriaClinicaInline(admin.StackedInline):
    model = HistoriaClinica
    extra = 0
    max_num = 1

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('mascota_id', 'nombre', 'especie', 'raza', 'propietario', 'sexo', 'activo')
    search_fields = ('nombre', 'especie', 'raza', 'propietario__nombres', 'propietario__apellidos', 'propietario__documento')
    list_filter = ('especie', 'sexo', 'activo')
    inlines = (HistoriaClinicaInline, AplicacionVacunaInline)

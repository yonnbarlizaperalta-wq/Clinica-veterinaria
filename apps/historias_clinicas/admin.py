from django.contrib import admin
from .models import HistoriaClinica
@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    list_display = ('historia_id', 'mascota', 'fecha_apertura')
    search_fields = ('mascota__nombre', 'mascota__propietario__apellidos', 'alergias', 'antecedentes')
    list_filter = ('fecha_apertura',)

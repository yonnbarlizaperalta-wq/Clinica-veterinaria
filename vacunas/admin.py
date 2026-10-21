from django.contrib import admin
from .models import Vacuna
@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    list_display = ('vacuna_id', 'nombre', 'especie_objetivo', 'fabricante', 'intervalo_meses', 'activa')
    search_fields = ('nombre', 'especie_objetivo', 'fabricante')
    list_filter = ('especie_objetivo', 'activa')

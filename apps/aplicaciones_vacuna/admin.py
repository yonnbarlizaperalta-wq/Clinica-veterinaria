from django.contrib import admin
from .models import AplicacionVacuna
class AplicacionVacunaInline(admin.TabularInline):
    model = AplicacionVacuna
    extra = 0
    autocomplete_fields = ('vacuna', 'veterinario')
@admin.register(AplicacionVacuna)
class AplicacionVacunaAdmin(admin.ModelAdmin):
    list_display = ('aplicacion_id', 'fecha', 'mascota', 'vacuna', 'dosis', 'veterinario', 'proxima_fecha')
    search_fields = ('mascota__nombre', 'vacuna__nombre', 'lote', 'veterinario__apellidos')
    list_filter = ('fecha', 'vacuna', 'veterinario')
    autocomplete_fields = ('mascota', 'vacuna', 'veterinario')

from django.contrib import admin
from .models import Cita
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('cita_id', 'fecha_hora', 'mascota', 'veterinario', 'motivo', 'estado')
    search_fields = ('mascota__nombre', 'veterinario__nombres', 'veterinario__apellidos', 'motivo')
    list_filter = ('estado', 'fecha_hora', 'veterinario')
    date_hierarchy = 'fecha_hora'

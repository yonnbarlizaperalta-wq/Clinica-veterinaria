from django.contrib import admin
from .models import Veterinario
@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('veterinario_id', 'nombres', 'apellidos', 'documento', 'especialidad', 'telefono', 'activo')
    search_fields = ('nombres', 'apellidos', 'documento', 'tarjeta_profesional', 'especialidad')
    list_filter = ('especialidad', 'activo')

from django.contrib import admin
from .models import Propietario
from mascotas.models import Mascota

class MascotaInline(admin.TabularInline):
    model = Mascota
    extra = 0
    show_change_link = True

@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ('propietario_id', 'nombres', 'apellidos', 'documento', 'telefono', 'correo')
    search_fields = ('nombres', 'apellidos', 'documento', 'telefono', 'correo')
    list_filter = ('apellidos',)
    inlines = (MascotaInline,)

from django.contrib import admin
from django.urls import path

from . import views
admin.site.site_header = 'Clínica veterinaria Huellitas | Administración'
admin.site.site_title = 'Huellitas'
admin.site.index_title = 'Gestión de la clínica'
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear-cuenta/', views.registrar, name='registrar'),
    path('acceder/', views.ingresar, name='ingresar'),
    path('salir/', views.cerrar_sesion, name='cerrar_sesion'),
    path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
    path('mi-cuenta/mascotas/nueva/', views.nueva_mascota, name='nueva_mascota'),
    path('mi-cuenta/citas/nueva/', views.nueva_cita, name='nueva_cita'),
    path('mi-cuenta/calendario/', views.calendario, name='calendario'),
    path('mi-cuenta/mascotas/<int:mascota_id>/historia/', views.historia_mascota, name='historia_mascota'),
    path('personal/', views.agenda_personal, name='agenda_personal'),
    path('personal/citas/nueva/', views.nueva_cita_personal, name='nueva_cita_personal'),
    path('personal/citas/<int:cita_id>/', views.atender_cita, name='atender_cita'),
    path('personal/vacunas/nueva/', views.registrar_vacuna, name='registrar_vacuna'),
    path('personal/calendario/', views.calendario, name='calendario_personal'),
    path('admin/', admin.site.urls),
]

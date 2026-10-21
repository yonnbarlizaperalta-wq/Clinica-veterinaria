from django.contrib import admin
from django.urls import path
admin.site.site_header = 'Clínica veterinaria Huellitas | Administración'
admin.site.site_title = 'Huellitas'
admin.site.index_title = 'Gestión de la clínica'
urlpatterns = [path('admin/', admin.site.urls)]

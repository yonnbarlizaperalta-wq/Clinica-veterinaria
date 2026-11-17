from django.urls import path

from . import views

app_name = 'citas'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nueva/', views.crear, name='crear'),
    path('<int:cita_id>/', views.detalle, name='detalle'),
    path('<int:cita_id>/editar/', views.editar, name='editar'),
    path('<int:cita_id>/eliminar/', views.eliminar, name='eliminar'),
]

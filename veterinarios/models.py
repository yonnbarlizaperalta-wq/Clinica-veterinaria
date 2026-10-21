from django.db import models
class Veterinario(models.Model):
    veterinario_id = models.BigAutoField(primary_key=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    documento = models.CharField(max_length=20, unique=True)
    tarjeta_profesional = models.CharField(max_length=40, unique=True)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(unique=True)
    especialidad = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)
    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = 'veterinario'
        verbose_name_plural = 'veterinarios'
    def __str__(self):
        return f'Dr(a). {self.nombres} {self.apellidos}'

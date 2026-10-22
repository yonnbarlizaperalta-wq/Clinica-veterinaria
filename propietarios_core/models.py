from django.db import models
class Propietario(models.Model):
    propietario_id = models.BigAutoField(primary_key=True)
    usuario = models.OneToOneField('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='perfil_propietario')
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    documento = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=160)
    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = 'propietario'
        verbose_name_plural = 'propietarios'
    def __str__(self):
        return f'{self.nombres} {self.apellidos} ({self.documento})'

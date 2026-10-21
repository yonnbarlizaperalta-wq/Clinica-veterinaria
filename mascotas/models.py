from django.db import models
class Mascota(models.Model):
    mascota_id = models.BigAutoField(primary_key=True)
    propietario = models.ForeignKey('propietarios_core.Propietario', on_delete=models.PROTECT, related_name='mascotas')
    nombre = models.CharField(max_length=80)
    especie = models.CharField(max_length=40)
    raza = models.CharField(max_length=60, blank=True)
    sexo = models.CharField(max_length=10, choices=[('M', 'Macho'), ('H', 'Hembra')])
    fecha_nacimiento = models.DateField(null=True, blank=True)
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    activo = models.BooleanField(default=True)
    class Meta:
        ordering = ['nombre']
        verbose_name = 'mascota'
        verbose_name_plural = 'mascotas'
    def __str__(self):
        return f'{self.nombre} — {self.especie}'

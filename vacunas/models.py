from django.db import models
class Vacuna(models.Model):
    vacuna_id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    especie_objetivo = models.CharField(max_length=40)
    fabricante = models.CharField(max_length=100, blank=True)
    intervalo_meses = models.PositiveSmallIntegerField(default=12)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    class Meta:
        ordering = ['nombre']
        verbose_name = 'vacuna'
        verbose_name_plural = 'vacunas'
    def __str__(self):
        return f'{self.nombre} ({self.especie_objetivo})'

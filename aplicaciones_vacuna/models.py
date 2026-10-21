from django.db import models
class AplicacionVacuna(models.Model):
    aplicacion_id = models.BigAutoField(primary_key=True)
    mascota = models.ForeignKey('mascotas.Mascota', on_delete=models.CASCADE, related_name='aplicaciones_vacuna')
    vacuna = models.ForeignKey('vacunas.Vacuna', on_delete=models.PROTECT, related_name='aplicaciones')
    veterinario = models.ForeignKey('veterinarios.Veterinario', on_delete=models.PROTECT, related_name='vacunaciones')
    fecha = models.DateField()
    dosis = models.CharField(max_length=40)
    lote = models.CharField(max_length=60, blank=True)
    proxima_fecha = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    class Meta:
        ordering = ['-fecha']
        constraints = [models.UniqueConstraint(fields=['mascota', 'vacuna', 'fecha'], name='unique_vaccine_per_pet_date')]
        verbose_name = 'aplicación de vacuna'
        verbose_name_plural = 'aplicaciones de vacunas'
    def __str__(self):
        return f'{self.vacuna} — {self.mascota} — {self.fecha:%d/%m/%Y}'

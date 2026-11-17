from django.db import models
class AplicacionVacuna(models.Model):
    aplicacion_id = models.BigAutoField(primary_key=True, db_column='pk_aplicacion_id')
    mascota = models.ForeignKey('mascotas.Mascota', on_delete=models.CASCADE, related_name='aplicaciones_vacuna', db_column='fk_mascota_id')
    vacuna = models.ForeignKey('vacunas.Vacuna', on_delete=models.PROTECT, related_name='aplicaciones', db_column='fk_vacuna_id')
    veterinario = models.ForeignKey('veterinarios.Veterinario', on_delete=models.PROTECT, related_name='vacunaciones', db_column='fk_veterinario_id')
    fecha = models.DateField()
    dosis = models.CharField(max_length=40)
    lote = models.CharField(max_length=60, blank=True)
    proxima_fecha = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    class Meta:
        db_table = 'tbl_aplicacion_vacuna'
        ordering = ['-fecha']
        constraints = [models.UniqueConstraint(fields=['mascota', 'vacuna', 'fecha'], name='unique_vaccine_per_pet_date')]
        verbose_name = 'aplicación de vacuna'
        verbose_name_plural = 'aplicaciones de vacunas'
    def __str__(self):
        return f'{self.vacuna} — {self.mascota} — {self.fecha:%d/%m/%Y}'

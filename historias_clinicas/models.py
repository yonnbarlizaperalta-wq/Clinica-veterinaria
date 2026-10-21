from django.db import models
class HistoriaClinica(models.Model):
    historia_id = models.BigAutoField(primary_key=True)
    mascota = models.OneToOneField('mascotas.Mascota', on_delete=models.CASCADE, related_name='historia_clinica')
    fecha_apertura = models.DateField()
    alergias = models.TextField(blank=True)
    antecedentes = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    class Meta:
        verbose_name = 'historia clínica'
        verbose_name_plural = 'historias clínicas'
    def __str__(self):
        return f'Historia de {self.mascota}'

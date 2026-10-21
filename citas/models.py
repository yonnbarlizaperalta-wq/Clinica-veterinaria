from django.db import models
class Cita(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        ATENDIDA = 'ATENDIDA', 'Atendida'
        CANCELADA = 'CANCELADA', 'Cancelada'
    cita_id = models.BigAutoField(primary_key=True)
    mascota = models.ForeignKey('mascotas.Mascota', on_delete=models.PROTECT, related_name='citas')
    veterinario = models.ForeignKey('veterinarios.Veterinario', on_delete=models.PROTECT, related_name='citas')
    fecha_hora = models.DateTimeField()
    motivo = models.CharField(max_length=180)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PROGRAMADA)
    notas = models.TextField(blank=True)
    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'cita'
        verbose_name_plural = 'citas'
    def __str__(self):
        return f'{self.mascota} — {self.fecha_hora:%d/%m/%Y %H:%M}'

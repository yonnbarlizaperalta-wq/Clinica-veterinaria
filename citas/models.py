from django.db import models


class Cita(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        ATENDIDA = 'ATENDIDA', 'Atendida'
        CANCELADA = 'CANCELADA', 'Cancelada'

    cita_id = models.BigAutoField(
        primary_key=True,
        db_column='pk_cita_id',
    )
    mascota = models.ForeignKey(
        'mascotas.Mascota',
        on_delete=models.PROTECT,
        related_name='citas',
        db_column='fk_mascota_id',
    )
    veterinario = models.ForeignKey(
        'veterinarios.Veterinario',
        on_delete=models.PROTECT,
        related_name='citas',
        db_column='fk_veterinario_id',
    )
    fecha_hora = models.DateTimeField()
    motivo = models.CharField(max_length=180)
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.PROGRAMADA,
    )
    notas = models.TextField(blank=True)

    class Meta:
        db_table = 'tbl_cita'
        ordering = ['-fecha_hora']
        verbose_name = 'cita'
        verbose_name_plural = 'citas'

    def __str__(self):
        fecha = self.fecha_hora.strftime('%d/%m/%Y %H:%M')
        return f'{self.mascota} — {fecha}'

from django import forms

from mascotas.models import Mascota
from veterinarios.models import Veterinario
from .models import Cita


class CitaForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local', 'class': 'form-control'},
        ),
    )

    class Meta:
        model = Cita
        fields = ['mascota', 'veterinario', 'fecha_hora', 'motivo', 'estado', 'notas']
        labels = {
            'mascota': 'Mascota',
            'veterinario': 'Veterinario',
            'fecha_hora': 'Fecha y hora',
            'motivo': 'Motivo de la cita',
            'estado': 'Estado',
            'notas': 'Notas de atención',
        }
        widgets = {
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mascota': forms.Select(attrs={'class': 'form-select'}),
            'veterinario': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, veterinario_usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mascota'].queryset = Mascota.objects.filter(activo=True).order_by('nombre')
        if veterinario_usuario:
            self.fields['veterinario'].queryset = Veterinario.objects.filter(usuario=veterinario_usuario, activo=True)
        else:
            self.fields['veterinario'].queryset = Veterinario.objects.filter(activo=True)

    def clean(self):
        datos = super().clean()
        veterinario = datos.get('veterinario')
        fecha_hora = datos.get('fecha_hora')

        if veterinario and fecha_hora:
            citas_ocupadas = Cita.objects.filter(
                veterinario=veterinario,
                fecha_hora=fecha_hora,
            ).exclude(estado=Cita.Estado.CANCELADA)

            if self.instance.pk:
                citas_ocupadas = citas_ocupadas.exclude(pk=self.instance.pk)

            if citas_ocupadas.exists():
                self.add_error('fecha_hora', 'Ese veterinario ya tiene una cita en ese horario.')

        return datos

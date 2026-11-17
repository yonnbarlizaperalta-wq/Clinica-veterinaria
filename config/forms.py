from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from aplicaciones_vacuna.models import AplicacionVacuna
from citas.models import Cita
from historias_clinicas.models import HistoriaClinica
from mascotas.models import Mascota
from propietarios_core.models import Propietario
from vacunas.models import Vacuna
from veterinarios.models import Veterinario


User = get_user_model()


class RegistroPropietarioForm(forms.Form):
    correo = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(
        label='Contraseña',
        min_length=8,
        widget=forms.PasswordInput,
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput,
    )
    nombres = forms.CharField(label='Nombres', max_length=80)
    apellidos = forms.CharField(label='Apellidos', max_length=80)
    documento = forms.CharField(label='Documento', max_length=20)
    telefono = forms.CharField(label='Teléfono', max_length=20)
    direccion = forms.CharField(label='Dirección', max_length=160)
    mascota_nombre = forms.CharField(label='Nombre de tu mascota', max_length=80)
    especie = forms.ChoiceField(
        label='Especie',
        choices=[('Canino', 'Perro'), ('Felino', 'Gato'), ('Ave', 'Ave'), ('Otro', 'Otro')],
    )
    raza = forms.CharField(label='Raza', max_length=60, required=False)
    sexo = forms.ChoiceField(
        label='Sexo',
        choices=[('M', 'Macho'), ('H', 'Hembra')],
    )
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento (opcional)',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip().lower()
        usuario_existe = User.objects.filter(username__iexact=correo).exists()
        correo_existe = User.objects.filter(email__iexact=correo).exists()

        if usuario_existe or correo_existe:
            raise forms.ValidationError(
                'Ya existe una cuenta con este correo. Inicia sesión o usa otro correo.'
            )

        return correo

    def clean_documento(self):
        documento = self.cleaned_data['documento'].strip()

        if Propietario.objects.filter(documento=documento).exists():
            raise forms.ValidationError(
                'Ya existe un propietario con este documento. '
                'Contacta a recepción para vincular tu cuenta.'
            )

        return documento

    def clean(self):
        datos = super().clean()
        password = datos.get('password')
        password_confirm = datos.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')

        return datos


class NuevaMascotaForm(forms.ModelForm):
    especie = forms.ChoiceField(
        label='Especie',
        choices=[('Canino', 'Perro'), ('Felino', 'Gato'), ('Ave', 'Ave'), ('Otro', 'Otro')],
    )
    sexo = forms.ChoiceField(
        label='Sexo',
        choices=[('M', 'Macho'), ('H', 'Hembra')],
    )

    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'sexo', 'fecha_nacimiento', 'peso_kg']
        labels = {
            'nombre': 'Nombre',
            'raza': 'Raza',
            'fecha_nacimiento': 'Fecha de nacimiento (opcional)',
            'peso_kg': 'Peso en kg (opcional)',
        }
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'peso_kg': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, propietario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.propietario = propietario

    def save(self, commit=True):
        mascota = super().save(commit=False)
        mascota.propietario = self.propietario

        if commit:
            mascota.save()
            HistoriaClinica.objects.create(
                mascota=mascota,
                fecha_apertura=timezone.localdate(),
                observaciones='Historia clínica iniciada al registrar la mascota.',
            )

        return mascota


class NuevaCitaForm(forms.Form):
    mascota = forms.ModelChoiceField(
        queryset=Mascota.objects.none(),
        label='Mascota',
    )
    veterinario = forms.ModelChoiceField(
        queryset=Veterinario.objects.none(),
        label='Veterinario',
    )
    fecha = forms.DateField(
        label='Fecha',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'min': timezone.localdate().isoformat(),
        }),
    )
    hora = forms.TimeField(
        label='Hora',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'min': '08:00',
            'max': '18:00',
        }),
    )
    motivo = forms.CharField(
        label='Motivo de la consulta',
        max_length=180,
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, propietario=None, personal=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.propietario = propietario
        self.personal = personal

        if personal:
            self.fields['mascota'].queryset = Mascota.objects.filter(activo=True)
            self.fields['propietario'] = forms.ModelChoiceField(
                queryset=Propietario.objects.order_by('apellidos', 'nombres'),
                label='Propietario',
            )
            self.order_fields([
                'propietario', 'mascota', 'veterinario', 'fecha', 'hora', 'motivo',
            ])
        else:
            self.fields['mascota'].queryset = Mascota.objects.filter(
                propietario=propietario,
                activo=True,
            )

        self.fields['veterinario'].queryset = Veterinario.objects.filter(activo=True)

    def clean(self):
        datos = super().clean()

        if self.personal:
            propietario = datos.get('propietario')
        else:
            propietario = self.propietario

        mascota = datos.get('mascota')
        if propietario and mascota and mascota.propietario_id != propietario.propietario_id:
            self.add_error('mascota', 'La mascota no pertenece al propietario seleccionado.')

        return datos

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']

        if fecha < timezone.localdate():
            raise forms.ValidationError('Elige hoy o una fecha futura.')

        return fecha


class ReprogramarCitaForm(forms.Form):
    fecha = forms.DateField(
        label='Nueva fecha',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'min': timezone.localdate().isoformat(),
        }),
    )
    hora = forms.TimeField(
        label='Nueva hora',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'min': '08:00',
            'max': '18:00',
        }),
    )

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']

        if fecha < timezone.localdate():
            raise forms.ValidationError('Elige hoy o una fecha futura.')

        return fecha


class ActualizarCitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['estado', 'notas']
        labels = {
            'estado': 'Estado de la cita',
            'notas': 'Nota clínica de la consulta',
        }
        widgets = {
            'notas': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Síntomas, evaluación, tratamiento y recomendaciones…',
            }),
        }


class HistoriaClinicaForm(forms.ModelForm):
    class Meta:
        model = HistoriaClinica
        fields = ['alergias', 'antecedentes', 'observaciones']
        labels = {
            'alergias': 'Alergias',
            'antecedentes': 'Antecedentes médicos',
            'observaciones': 'Observaciones generales',
        }
        widgets = {
            'alergias': forms.Textarea(attrs={'rows': 3}),
            'antecedentes': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }


class AplicacionVacunaForm(forms.ModelForm):
    class Meta:
        model = AplicacionVacuna
        fields = [
            'mascota', 'vacuna', 'veterinario', 'fecha', 'dosis', 'lote',
            'proxima_fecha', 'observaciones',
        ]
        labels = {
            'mascota': 'Mascota',
            'vacuna': 'Vacuna',
            'veterinario': 'Veterinario',
            'fecha': 'Fecha de aplicación',
            'dosis': 'Dosis',
            'lote': 'Lote',
            'proxima_fecha': 'Próxima aplicación',
            'observaciones': 'Observaciones',
        }
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'proxima_fecha': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, veterinario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mascota'].queryset = Mascota.objects.filter(activo=True)
        self.fields['vacuna'].queryset = Vacuna.objects.filter(activa=True)
        self.fields['veterinario'].queryset = Veterinario.objects.filter(activo=True)

        if veterinario:
            self.fields['veterinario'].queryset = Veterinario.objects.filter(pk=veterinario.pk)
            self.fields['veterinario'].initial = veterinario

    def clean(self):
        datos = super().clean()
        mascota = datos.get('mascota')
        vacuna = datos.get('vacuna')
        fecha = datos.get('fecha')
        proxima_fecha = datos.get('proxima_fecha')

        if mascota and vacuna:
            especie_vacuna = vacuna.especie_objetivo.lower()
            especie_mascota = mascota.especie.lower()

            if especie_vacuna not in ['todas', 'general'] and especie_vacuna != especie_mascota:
                self.add_error(
                    'vacuna',
                    'Esta vacuna está indicada para ' + vacuna.especie_objetivo
                    + ', no para la especie seleccionada.',
                )

        if fecha and proxima_fecha and proxima_fecha < fecha:
            self.add_error(
                'proxima_fecha',
                'La fecha de próxima aplicación debe ser posterior a la fecha de aplicación.',
            )

        return datos

from django import forms
from .models import Encomienda
from clientes.models import Cliente
from rutas.models import Ruta


class EncomiendaForm(forms.ModelForm):

    class Meta:
        model = Encomienda
        fields = [
            'codigo',
            'descripcion',
            'peso',
            'remitente',
            'destinatario',
            'ruta',
            'estado',
            'fecha_entrega'
        ]

        widgets = {
            'descripcion': forms.Textarea(
                attrs={
                    'rows': 5,
                    'class': 'form-control',
                    'placeholder': 'Descripción breve de la encomienda'
                }
            ),
            'peso': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0.01'
                }
            ),
            'estado': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'fecha_entrega': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['remitente'].queryset = Cliente.objects.filter(estado=1)
        self.fields['destinatario'].queryset = Cliente.objects.filter(estado=1)
        self.fields['ruta'].queryset = Ruta.objects.all()

        for name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.DateTimeInput)):
                    field.widget.attrs.update({'class': 'form-control'})
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs.update({'class': 'form-select'})
                elif isinstance(field.widget, forms.Textarea):
                    field.widget.attrs.update({'class': 'form-control', 'rows': 5})
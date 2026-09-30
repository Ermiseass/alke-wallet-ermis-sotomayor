from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente, Cuenta, Transaccion
class RegistroForm(UserCreationForm):
    nombre = forms.CharField(max_length=100)
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'nombre', 'email', 'password1', 'password2']
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Cliente.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'telefono', 'contactos']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contactos'].queryset = Cliente.objects.exclude(pk=self.instance.pk)
class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['alias']
class OperacionForm(forms.Form):
    cuenta = forms.ModelChoiceField(queryset=Cuenta.objects.none(), label='Mi cuenta')
    tipo = forms.ChoiceField(choices=Transaccion.TIPOS)
    monto = forms.DecimalField(min_value=0.01, max_digits=14, decimal_places=2)
    destino_numero = forms.UUIDField(required=False, label='Número UUID de destino (solo transferencias)')
    descripcion = forms.CharField(max_length=160, required=False, label='Descripción')
    def __init__(self, *args, usuario, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cuenta'].queryset = Cuenta.objects.filter(cliente__usuario=usuario)
    def clean(self):
        data = super().clean()
        numero = data.get('destino_numero')
        if data.get('tipo') == 'transferencia':
            destino = Cuenta.objects.filter(numero=numero).first() if numero else None
            if destino is None:
                self.add_error('destino_numero', 'Ingrese el número de una cuenta existente.')
            else:
                data['destino_id'] = destino.pk
        elif numero:
            self.add_error('destino_numero', 'El destino solo corresponde a transferencias.')
        return data

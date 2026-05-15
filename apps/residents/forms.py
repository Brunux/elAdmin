from django import forms
from django.contrib.auth.models import User
from apps.core.mixins import TablerFormMixin
from .models import Resident, Invitation


class UserCreateForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_unusable_password()
        if commit:
            user.save()
        return user


class UserEditForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ResidentProfileForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = Resident
        fields = [
            'phone', 'resident_type', 'apartments',
            'move_in_date', 'move_out_date', 'photo',
            'emergency_contact_name', 'emergency_contact_phone', 'notes',
        ]
        widgets = {
            'move_in_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'move_out_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class InvitationForm(TablerFormMixin, forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email', 'resident_type', 'apartment']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario registrado con este correo.')
        if Invitation.objects.filter(email=email, is_used=False).exists():
            raise forms.ValidationError('Ya existe una invitación pendiente para este correo.')
        return email


class InviteAcceptForm(TablerFormMixin, forms.Form):
    first_name = forms.CharField(label='Nombre', max_length=100)
    last_name = forms.CharField(label='Apellido', max_length=100)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

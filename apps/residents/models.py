import uuid
from django.db import models
from django.contrib.auth.models import User
from apps.units.models import Apartment


class Resident(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
    ]
    TYPE_CHOICES = [
        ('owner', 'Propietario'),
        ('tenant', 'Inquilino'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resident', verbose_name='Usuario')
    phone = models.CharField('Teléfono', max_length=20, blank=True)
    resident_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, default='tenant')
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='active')
    apartments = models.ManyToManyField(Apartment, blank=True,
                                       related_name='residents', verbose_name='Apartamentos')
    move_in_date = models.DateField('Fecha de ingreso', null=True, blank=True)
    move_out_date = models.DateField('Fecha de salida', null=True, blank=True)
    photo = models.ImageField('Foto', upload_to='residents/', null=True, blank=True)
    emergency_contact_name = models.CharField('Contacto de emergencia', max_length=150, blank=True)
    emergency_contact_phone = models.CharField('Teléfono de emergencia', max_length=20, blank=True)
    notes = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Residente'
        verbose_name_plural = 'Residentes'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    # Proxy properties so templates keep working without changes
    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email


class Invitation(models.Model):
    TYPE_CHOICES = Resident.TYPE_CHOICES

    email = models.EmailField('Correo electrónico')
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='invitations', verbose_name='Apartamento')
    resident_type = models.CharField('Tipo de residente', max_length=20, choices=TYPE_CHOICES, default='tenant')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='sent_invitations', verbose_name='Invitado por')
    is_used = models.BooleanField('Usado', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Invitación'
        verbose_name_plural = 'Invitaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f'Invitación para {self.email}'

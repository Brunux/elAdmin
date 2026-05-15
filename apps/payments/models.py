from django.db import models
from apps.units.models import Apartment
from apps.residents.models import Resident


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('submitted', 'En revisión'),
        ('paid', 'Pagado'),
        ('overdue', 'Vencido'),
        ('cancelled', 'Cancelado'),
    ]
    TYPE_CHOICES = [
        ('maintenance', 'Mantenimiento'),
        ('extra', 'Extraordinaria'),
        ('other', 'Otro'),
    ]

    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='payments', verbose_name='Apartamento')
    resident = models.ForeignKey(Resident, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='payments', verbose_name='Residente')
    payment_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, default='maintenance')
    amount = models.DecimalField('Monto', max_digits=10, decimal_places=2)
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField('Fecha límite')
    paid_date = models.DateField('Fecha de pago', null=True, blank=True)
    period = models.CharField('Periodo', max_length=20, help_text='Ej: 2025-01')
    reference = models.CharField('Referencia', max_length=100, blank=True)
    receipt = models.FileField('Comprobante', upload_to='payments/receipts/', null=True, blank=True)
    notes = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-due_date']

    def __str__(self):
        return f'{self.apartment} - {self.period} - ${self.amount}'

    @property
    def status_color(self):
        return {
            'pending': 'warning',
            'submitted': 'blue',
            'paid': 'success',
            'overdue': 'danger',
            'cancelled': 'secondary',
        }.get(self.status, 'secondary')

    @property
    def status_icon(self):
        return {
            'pending': 'ti-clock',
            'submitted': 'ti-upload',
            'paid': 'ti-check',
            'overdue': 'ti-alert-triangle',
            'cancelled': 'ti-x',
        }.get(self.status, 'ti-circle')


class Invoice(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField('Número', max_length=50, unique=True)
    issued_at = models.DateTimeField('Emitida el', auto_now_add=True)
    html_content = models.TextField('Contenido HTML')

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-issued_at']

    def __str__(self):
        return self.invoice_number

from django.db import models
from apps.payments.models import Payment
from apps.towers.models import Tower


class SiteConfiguration(models.Model):
    # Monthly payment generation
    auto_payments_enabled = models.BooleanField('Generar pagos automáticamente', default=False)
    payment_due_day = models.PositiveSmallIntegerField(
        'Día de vencimiento', default=10,
        help_text='Día del mes en que vencen los pagos (1-28).'
    )
    payment_type = models.CharField(
        'Tipo de pago', max_length=20,
        choices=Payment.TYPE_CHOICES, default='maintenance'
    )

    # Overdue check
    overdue_check_enabled = models.BooleanField('Marcar pagos vencidos automáticamente', default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración'

    def __str__(self):
        return 'Configuración del sitio'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class TowerMaintenanceFee(models.Model):
    tower = models.OneToOneField(
        Tower, on_delete=models.CASCADE,
        related_name='maintenance_fee', verbose_name='Torre',
    )
    amount = models.DecimalField('Cuota de mantenimiento', max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cuota de mantenimiento'
        verbose_name_plural = 'Cuotas de mantenimiento'
        ordering = ['tower__name']

    def __str__(self):
        return f'{self.tower} — ${self.amount}'

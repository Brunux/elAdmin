from django.db import models
from apps.towers.models import Tower


class Apartment(models.Model):
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE, related_name='apartments', verbose_name='Torre')
    number = models.CharField('Número', max_length=20)
    floor = models.PositiveIntegerField('Piso')
    area_sqm = models.DecimalField('Área (m²)', max_digits=8, decimal_places=2, null=True, blank=True)
    monthly_fee = models.DecimalField('Cuota mensual', max_digits=10, decimal_places=2, default=0)
    notes = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Apartamento'
        verbose_name_plural = 'Apartamentos'
        ordering = ['tower', 'floor', 'number']
        unique_together = [['tower', 'number']]

    def __str__(self):
        return f'{self.tower.name}-{self.number} (Piso {self.floor})'

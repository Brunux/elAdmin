from django.db import models


class Tower(models.Model):
    name = models.CharField('Nombre', max_length=100)
    number = models.SmallIntegerField(verbose_name='Número')
    floors = models.PositiveIntegerField('Número de pisos')
    description = models.TextField('Descripción', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Torre'
        verbose_name_plural = 'Torres'
        ordering = ['name']

    def __str__(self):
        return f'Torre {self.number} — {self.name}'

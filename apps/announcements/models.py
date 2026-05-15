from django.db import models
from django.contrib.auth.models import User


class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]

    title = models.CharField('Título', max_length=200)
    content = models.TextField('Contenido')
    priority = models.CharField('Prioridad', max_length=10, choices=PRIORITY_CHOICES, default='normal')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Autor')
    is_active = models.BooleanField('Activo', default=True)
    publish_date = models.DateField('Fecha de publicación', auto_now_add=True)
    expiry_date = models.DateField('Fecha de expiración', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Anuncio'
        verbose_name_plural = 'Anuncios'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

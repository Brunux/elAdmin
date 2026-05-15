from django.db import models
from django.contrib.auth.models import User
from apps.units.models import Apartment
from apps.residents.models import Resident


class Issue(models.Model):
    CATEGORY_CHOICES = [
        ('plumbing', 'Plomería'),
        ('electrical', 'Eléctrico'),
        ('elevator', 'Elevador'),
        ('common_areas', 'Áreas comunes'),
        ('security', 'Seguridad'),
        ('noise', 'Ruido'),
        ('cleaning', 'Limpieza'),
        ('structural', 'Estructura'),
        ('other', 'Otro'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    STATUS_CHOICES = [
        ('open', 'Abierto'),
        ('in_progress', 'En proceso'),
        ('resolved', 'Resuelto'),
        ('closed', 'Cerrado'),
        ('duplicated', 'Duplicado'),
    ]

    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción')
    category = models.CharField('Categoría', max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField('Prioridad', max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='open')
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='issues', verbose_name='Apartamento')
    reported_by = models.ForeignKey(Resident, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='issues', verbose_name='Reportado por')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='assigned_issues', verbose_name='Asignado a')
    duplicate_of = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='duplicates', verbose_name='Duplicado de',
    )
    photo = models.ImageField('Foto', upload_to='issues/', null=True, blank=True)
    resolved_at = models.DateTimeField('Resuelto el', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} — {self.title}'

    @property
    def status_color(self):
        return {
            'open': 'red',
            'in_progress': 'yellow',
            'resolved': 'green',
            'closed': 'secondary',
            'duplicated': 'purple',
        }.get(self.status, 'secondary')

    @property
    def status_icon(self):
        return {
            'open': 'ti-circle',
            'in_progress': 'ti-progress',
            'resolved': 'ti-circle-check',
            'closed': 'ti-lock',
            'duplicated': 'ti-copy',
        }.get(self.status, 'ti-circle')

    @property
    def priority_color(self):
        return {
            'urgent': 'red',
            'high': 'orange',
            'normal': 'blue',
            'low': 'secondary',
        }.get(self.priority, 'secondary')

    @property
    def priority_icon(self):
        return {
            'urgent': 'ti-flame',
            'high': 'ti-arrow-up',
            'normal': 'ti-minus',
            'low': 'ti-arrow-down',
        }.get(self.priority, 'ti-minus')

    @property
    def resolution_days(self):
        if self.resolved_at and self.created_at:
            return (self.resolved_at - self.created_at).days
        return None


class IssueNote(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='notes')
    status = models.CharField('Estado', max_length=20, choices=Issue.STATUS_CHOICES)
    body = models.TextField('Nota', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'#{self.issue.pk} → {self.status}'

    @property
    def status_color(self):
        return {
            'open': 'red',
            'in_progress': 'yellow',
            'resolved': 'green',
            'closed': 'secondary',
            'duplicated': 'purple',
        }.get(self.status, 'secondary')

    @property
    def status_icon(self):
        return {
            'open': 'ti-circle',
            'in_progress': 'ti-progress',
            'resolved': 'ti-circle-check',
            'closed': 'ti-lock',
            'duplicated': 'ti-copy',
        }.get(self.status, 'ti-circle')

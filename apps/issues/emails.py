from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.urls import reverse


def _issue_url(request, issue):
    return request.build_absolute_uri(reverse('issues:detail', args=[issue.pk]))


def _staff_emails():
    return list(
        User.objects.filter(is_staff=True, is_active=True)
        .exclude(email='')
        .values_list('email', flat=True)
    )


def notify_staff_new_issue(request, issue):
    recipients = _staff_emails()
    if not recipients:
        return
    send_mail(
        subject=f'[El Admin] Nuevo reporte #{issue.pk}: {issue.title}',
        message=(
            f'Se ha creado un nuevo reporte.\n\n'
            f'Título: {issue.title}\n'
            f'Categoría: {issue.get_category_display()}\n'
            f'Prioridad: {issue.get_priority_display()}\n'
            f'Reportado por: {issue.reported_by or "—"}\n'
            f'Apartamento: {issue.apartment or "—"}\n\n'
            f'Ver reporte: {_issue_url(request, issue)}'
        ),
        from_email=None,
        recipient_list=recipients,
        fail_silently=True,
    )


def _notes_history(issue):
    lines = []
    for note in issue.notes.select_related('created_by').all():
        who = note.created_by.get_full_name() or note.created_by.username if note.created_by else '—'
        when = note.created_at.strftime('%d/%m/%Y %H:%M')
        lines.append(f'  [{when}] {who} — Estado: {note.get_status_display()}')
        if note.body:
            lines.append(f'    {note.body}')
    return '\n'.join(lines) if lines else '  Sin notas.'


def notify_staff_issue_reopened(request, issue, updated_by=None):
    recipients = _staff_emails()
    if not recipients:
        return
    who = updated_by.get_full_name() or updated_by.username if updated_by else '—'
    send_mail(
        subject=f'[El Admin] Reporte #{issue.pk} marcado como abierto: {issue.title}',
        message=(
            f'El reporte fue actualizado a "Abierto" por {who}.\n\n'
            f'Título: {issue.title}\n'
            f'Reportado por: {issue.reported_by or "—"}\n'
            f'Apartamento: {issue.apartment or "—"}\n\n'
            f'Historial de notas:\n{_notes_history(issue)}\n\n'
            f'Ver reporte: {_issue_url(request, issue)}'
        ),
        from_email=None,
        recipient_list=recipients,
        fail_silently=True,
    )


def notify_owner_status_changed(request, issue, updated_by=None):
    if not issue.reported_by:
        return
    email = issue.reported_by.user.email
    if not email:
        return
    who = updated_by.get_full_name() or updated_by.username if updated_by else '—'
    send_mail(
        subject=f'[El Admin] Tu reporte #{issue.pk} fue actualizado',
        message=(
            f'Tu reporte fue actualizado por {who}.\n\n'
            f'Título: {issue.title}\n'
            f'Estado: {issue.get_status_display()}\n'
            f'Prioridad: {issue.get_priority_display()}\n\n'
            f'Historial de notas:\n{_notes_history(issue)}\n\n'
            f'Ver reporte: {_issue_url(request, issue)}'
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=True,
    )

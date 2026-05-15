from django.core.mail import send_mass_mail
from django.conf import settings


def notify_residents_announcement(request, announcement, towers):
    from apps.residents.models import Resident
    recipients = (
        Resident.objects.filter(
            apartments__tower__in=towers,
            status='active',
        )
        .select_related('user')
        .distinct()
    )
    tower_names = ', '.join(str(t) for t in towers)
    subject = f'[El Admin] {announcement.title}'
    messages = []
    for resident in recipients:
        if not resident.user.email:
            continue
        body = (
            f'Hola {resident.user.first_name or resident.user.username},\n\n'
            f'Se ha publicado un nuevo anuncio en El Admin:\n\n'
            f'— {announcement.title} —\n\n'
            f'{announcement.content}\n\n'
            f'Torres notificadas: {tower_names}\n\n'
            f'Saludos,\nEl Admin'
        )
        messages.append((subject, body, settings.DEFAULT_FROM_EMAIL, [resident.user.email]))
    if messages:
        send_mass_mail(messages, fail_silently=True)
    return len(messages)

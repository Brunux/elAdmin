from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.urls import reverse


def _payment_url(request, payment):
    path = reverse('payments:detail', args=[payment.pk])
    if request:
        return request.build_absolute_uri(path)
    return path


def _staff_emails():
    return list(
        User.objects.filter(is_staff=True, is_active=True)
        .exclude(email='')
        .values_list('email', flat=True)
    )


def notify_owner_payment_pending(request, payment):
    if not payment.resident:
        return
    email = payment.resident.user.email
    if not email:
        return
    send_mail(
        subject=f'[El Admin] Nuevo pago pendiente — {payment.period}',
        message=(
            f'Se ha generado un nuevo pago pendiente para tu apartamento.\n\n'
            f'Apartamento: {payment.apartment}\n'
            f'Tipo: {payment.get_payment_type_display()}\n'
            f'Periodo: {payment.period}\n'
            f'Monto: ${payment.amount}\n'
            f'Fecha límite: {payment.due_date.strftime("%d/%m/%Y")}\n\n'
            f'Cuando realices el pago, ingresa al sistema y registra el comprobante:\n'
            f'{_payment_url(request, payment)}'
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=True,
    )


def notify_staff_payment_submitted(request, payment):
    recipients = _staff_emails()
    if not recipients:
        return
    send_mail(
        subject=f'[El Admin] Comprobante de pago enviado — {payment.apartment} {payment.period}',
        message=(
            f'Un residente ha registrado un comprobante de pago y está esperando confirmación.\n\n'
            f'Residente: {payment.resident or "—"}\n'
            f'Apartamento: {payment.apartment}\n'
            f'Periodo: {payment.period}\n'
            f'Monto: ${payment.amount}\n'
            f'Referencia: {payment.reference or "—"}\n'
            f'Fecha de pago: {payment.paid_date.strftime("%d/%m/%Y") if payment.paid_date else "—"}\n\n'
            f'Confirmar pago: {_payment_url(request, payment)}'
        ),
        from_email=None,
        recipient_list=recipients,
        fail_silently=True,
    )


def notify_owner_payment_confirmed(request, payment):
    if not payment.resident:
        return
    email = payment.resident.user.email
    if not email:
        return
    send_mail(
        subject=f'[El Admin] Pago confirmado — {payment.period}',
        message=(
            f'Tu pago ha sido confirmado por la administración.\n\n'
            f'Apartamento: {payment.apartment}\n'
            f'Periodo: {payment.period}\n'
            f'Monto: ${payment.amount}\n'
            f'Referencia: {payment.reference or "—"}\n\n'
            f'Ver detalle: {_payment_url(request, payment)}'
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=True,
    )

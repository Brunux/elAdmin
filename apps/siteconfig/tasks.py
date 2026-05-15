from datetime import date


def generate_monthly_payments():
    from apps.siteconfig.models import SiteConfiguration
    from apps.units.models import Apartment
    from apps.payments.models import Payment

    config = SiteConfiguration.get()
    if not config.auto_payments_enabled:
        return

    today = date.today()
    period = today.strftime('%Y-%m')
    due_date = today.replace(day=config.payment_due_day)

    apartments = Apartment.objects.filter(status='occupied').prefetch_related('residents')

    created = 0
    for apartment in apartments:
        # Link to the owner resident if one exists, else any active resident
        resident = (
            apartment.residents.filter(resident_type='owner', status='active').first()
            or apartment.residents.filter(status='active').first()
        )

        _, was_created = Payment.objects.get_or_create(
            apartment=apartment,
            period=period,
            payment_type=config.payment_type,
            defaults=dict(
                resident=resident,
                amount=apartment.monthly_fee,
                status='pending',
                due_date=due_date,
            ),
        )
        if was_created:
            created += 1
            # Notify owner — no request object in scheduled context, so skip URL building
            try:
                from apps.payments.emails import notify_owner_payment_pending
                notify_owner_payment_pending(None, payment)
            except Exception:
                pass

    print(f'[generate_monthly_payments] {period}: {created} payment(s) created.')


def check_overdue_payments():
    from apps.siteconfig.models import SiteConfiguration
    from apps.payments.models import Payment

    config = SiteConfiguration.get()
    if not config.overdue_check_enabled:
        return

    today = date.today()
    updated = Payment.objects.filter(status='pending', due_date__lt=today).update(status='overdue')
    print(f'[check_overdue_payments] {today}: {updated} payment(s) marked overdue.')

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


def start():
    from .tasks import generate_monthly_payments, check_overdue_payments

    scheduler = BackgroundScheduler()

    # 1st of every month at 10:00
    scheduler.add_job(
        generate_monthly_payments,
        trigger=CronTrigger(day=1, hour=10, minute=0),
        id='generate_monthly_payments',
        replace_existing=True,
    )

    # Every day at 10:00
    scheduler.add_job(
        check_overdue_payments,
        trigger=CronTrigger(hour=10, minute=0),
        id='check_overdue_payments',
        replace_existing=True,
    )

    scheduler.start()

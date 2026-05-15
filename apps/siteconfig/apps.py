import os
from django.apps import AppConfig


class SiteconfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.siteconfig'
    label = 'siteconfig'

    def ready(self):
        # Only start scheduler in the main process (not the reloader watcher)
        if os.environ.get('RUN_MAIN') != 'true':
            return
        from .scheduler import start
        start()

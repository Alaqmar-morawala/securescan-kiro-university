"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Vercel's Python runtime looks for a variable named ``app``.
app = application

# Serverless demo DB is ephemeral (SQLite in /tmp): create the schema on
# cold start so register/add/scan/report works with zero external services.
if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command

        call_command('migrate', run_syncdb=True, verbosity=0)
    except Exception:
        # Never block the app from booting if migration fails.
        pass

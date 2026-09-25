"""Manage the local ZAP daemon used by the real scan engine.

    python manage.py zap up       # start (or reuse) a daemon, wait until ready
    python manage.py zap status   # probe + show engine configuration
    python manage.py zap stop     # stop a daemon this tool started

The daemon binds 127.0.0.1 only; with no SECURESCAN_ZAP_API_KEY set it runs
with api.disablekey=true, which is safe for a local single-user demo.
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from scanner import zap_process


class Command(BaseCommand):
    help = "Manage the local ZAP daemon (up/status/stop)."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["up", "status", "stop"])

    def handle(self, *args, **options):
        action = options["action"]
        host = settings.SECURESCAN_ZAP_HOST
        port = settings.SECURESCAN_ZAP_PORT
        api_key = settings.SECURESCAN_ZAP_API_KEY

        if action == "status":
            if zap_process.zap_ready(host, port, api_key):
                self.stdout.write(self.style.SUCCESS(f"ZAP ready at {host}:{port}"))
            else:
                self.stdout.write(f"ZAP not reachable at {host}:{port}")
            return

        if action == "up":
            if zap_process.zap_ready(host, port, api_key):
                self.stdout.write(self.style.SUCCESS(f"Reusing ZAP at {host}:{port}"))
                return
            if not zap_process.find_zap_binary():
                self.stderr.write(
                    "zaproxy binary not found on PATH "
                    "(apt install zaproxy, or set SECURESCAN_ZAP_HOST/PORT)."
                )
                raise SystemExit(1)
            zap_process.start_daemon(
                host, port, api_key, settings.SECURESCAN_ZAP_BOOT_TIMEOUT_S
            )
            self.stdout.write(
                self.style.SUCCESS(f"ZAP daemon ready at {host}:{port}")
            )
            return

        # stop
        if zap_process.stop_daemon(port):
            self.stdout.write(f"Stop signal sent to pidfile-tracked ZAP on {port}")
        else:
            self.stdout.write(
                f"No pidfile-tracked ZAP daemon on {port} "
                "(a manually started daemon is left untouched)."
            )

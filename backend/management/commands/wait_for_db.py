"""
Django management command to wait for database to be ready
Useful for Docker containers and CI/CD
"""
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    help = 'Wait for database to be available'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Maximum wait time in seconds (default: 60)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=1,
            help='Check interval in seconds (default: 1)',
        )

    def handle(self, *args, **options):
        timeout = options['timeout']
        interval = options['interval']
        
        self.stdout.write('Waiting for database...')
        
        db_conn = connections['default']
        start_time = time.time()
        
        while True:
            try:
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS('✓ Database available!'))
                break
            except OperationalError:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Database not available after {timeout}s')
                    )
                    raise OperationalError(
                        f'Database not available after {timeout} seconds'
                    )
                
                self.stdout.write(
                    f'Database unavailable, waiting... ({int(elapsed)}s)'
                )
                time.sleep(interval)

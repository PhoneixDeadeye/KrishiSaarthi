"""
Django management command to validate environment configuration
Usage: python manage.py validate_environment
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys


class Command(BaseCommand):
    help = 'Validates environment configuration for production readiness'

    def add_arguments(self, parser):
        parser.add_argument(
            '--strict',
            action='store_true',
            help='Fail on warnings (for CI/CD)',
        )

    def handle(self, *args, **options):
        strict = options['strict']
        errors = []
        warnings = []
        
        self.stdout.write(self.style.SUCCESS('🔍 Environment Validation\n'))
        self.stdout.write('=' * 60)
        
        # Check SECRET_KEY
        self.stdout.write('\n1. SECRET_KEY')
        if not settings.SECRET_KEY or settings.SECRET_KEY == 'your-secret-key-here':
            errors.append('SECRET_KEY not configured or using default value')
            self.stdout.write(self.style.ERROR('   ✗ Not configured'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ Configured'))
        
        # Check DEBUG setting
        self.stdout.write('\n2. DEBUG Mode')
        if settings.DEBUG:
            warnings.append('DEBUG is True (should be False in production)')
            self.stdout.write(self.style.WARNING('   ⚠ True (development mode)'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ False (production mode)'))
        
        # Check ALLOWED_HOSTS
        self.stdout.write('\n3. ALLOWED_HOSTS')
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            warnings.append('ALLOWED_HOSTS is too permissive')
            self.stdout.write(self.style.WARNING('   ⚠ Too permissive'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✓ {", ".join(settings.ALLOWED_HOSTS)}'))
        
        # Check database
        self.stdout.write('\n4. Database')
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'sqlite' in db_engine and not settings.DEBUG:
            warnings.append('Using SQLite in production (consider PostgreSQL)')
            self.stdout.write(self.style.WARNING('   ⚠ SQLite (consider PostgreSQL for production)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✓ {db_engine}'))
        
        # Check API keys
        self.stdout.write('\n5. API Keys')
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        weather_key = os.getenv('OPENWEATHER_API_KEY', '')
        
        if not gemini_key or gemini_key == 'your-gemini-api-key-here':
            warnings.append('GEMINI_API_KEY not configured')
            self.stdout.write(self.style.WARNING('   ⚠ Gemini API key missing'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ Gemini API key configured'))
        
        if not weather_key or weather_key == 'your-openweather-api-key-here':
            warnings.append('OPENWEATHER_API_KEY not configured')
            self.stdout.write(self.style.WARNING('   ⚠ OpenWeather API key missing'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ OpenWeather API key configured'))
        
        # Check CORS
        self.stdout.write('\n6. CORS Configuration')
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        if not cors_origins:
            errors.append('CORS_ALLOWED_ORIGINS not configured')
            self.stdout.write(self.style.ERROR('   ✗ Not configured'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✓ {len(cors_origins)} origins allowed'))
        
        # Check static files
        self.stdout.write('\n7. Static Files')
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            self.stdout.write(self.style.SUCCESS('   ✓ STATIC_ROOT configured'))
        else:
            warnings.append('STATIC_ROOT not configured')
            self.stdout.write(self.style.WARNING('   ⚠ STATIC_ROOT not configured'))
        
        # Check media files
        self.stdout.write('\n8. Media Files')
        if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
            self.stdout.write(self.style.SUCCESS('   ✓ MEDIA_ROOT configured'))
        else:
            warnings.append('MEDIA_ROOT not configured')
            self.stdout.write(self.style.WARNING('   ⚠ MEDIA_ROOT not configured'))
        
        # Check logging
        self.stdout.write('\n9. Logging')
        if hasattr(settings, 'LOGGING') and settings.LOGGING:
            self.stdout.write(self.style.SUCCESS('   ✓ Logging configured'))
        else:
            warnings.append('Logging not configured')
            self.stdout.write(self.style.WARNING('   ⚠ Logging not configured'))
        
        # Check email
        self.stdout.write('\n10. Email Backend')
        email_backend = settings.EMAIL_BACKEND
        if 'console' in email_backend and not settings.DEBUG:
            warnings.append('Using console email backend in production')
            self.stdout.write(self.style.WARNING('   ⚠ Console backend (configure SMTP for production)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✓ {email_backend}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('\n📊 Summary\n')
        
        if errors:
            self.stdout.write(self.style.ERROR(f'✗ Errors: {len(errors)}'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  • {error}'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ No critical errors'))
        
        if warnings:
            self.stdout.write(self.style.WARNING(f'\n⚠ Warnings: {len(warnings)}'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'  • {warning}'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ No warnings'))
        
        self.stdout.write('\n' + '=' * 60 + '\n')
        
        # Exit code
        if errors:
            self.stdout.write(self.style.ERROR('❌ Environment validation failed'))
            sys.exit(1)
        elif warnings and strict:
            self.stdout.write(self.style.WARNING('⚠ Warnings found in strict mode'))
            sys.exit(1)
        else:
            self.stdout.write(self.style.SUCCESS('✅ Environment validation passed'))
            sys.exit(0)

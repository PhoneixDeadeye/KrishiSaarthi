#!/usr/bin/env python
"""
Database initialization and management script for KrishiSaarthi
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KrishiSaarthi.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection


def check_database():
    """Check if database is accessible"""
    try:
        connection.ensure_connection()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def run_migrations():
    """Run database migrations"""
    print("\n📦 Running database migrations...")
    try:
        call_command('makemigrations', interactive=False)
        call_command('migrate', interactive=False)
        print("✓ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False


def create_superuser():
    """Create a superuser if it doesn't exist"""
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@krishisaarthi.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    
    if not password:
        print("⚠️  DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation.")
        print("   Set the DJANGO_SUPERUSER_PASSWORD environment variable to create a superuser.")
        return True  # Not a failure — just skipped
    
    if User.objects.filter(username=username).exists():
        print(f"✓ Superuser '{username}' already exists")
        return True
    
    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✓ Superuser '{username}' created successfully")
        print(f"  Username: {username}")
        print("  ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!")
        return True
    except Exception as e:
        print(f"✗ Failed to create superuser: {e}")
        return False


def collect_static():
    """Collect static files"""
    print("\n📁 Collecting static files...")
    try:
        call_command('collectstatic', interactive=False, clear=True)
        print("✓ Static files collected")
        return True
    except Exception as e:
        print(f"⚠️  Static files collection skipped: {e}")
        return True  # Not critical


def initialize_database():
    """Main database initialization function"""
    print("=" * 60)
    print("KrishiSaarthi Database Initialization")
    print("=" * 60)
    
    success = True
    
    # Check database connection
    if not check_database():
        return False
    
    # Run migrations
    if not run_migrations():
        success = False
    
    # Create superuser
    if not create_superuser():
        success = False
    
    # Collect static files
    collect_static()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Database initialization completed successfully!")
    else:
        print("⚠️  Database initialization completed with warnings")
    print("=" * 60)
    
    return success


if __name__ == '__main__':
    initialize_database()

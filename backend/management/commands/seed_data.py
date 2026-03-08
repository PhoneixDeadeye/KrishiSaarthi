"""
Django management command to seed the database with sample data
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from field.models import FieldData, FieldLog
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Seeds the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of test users to create'
        )
        parser.add_argument(
            '--fields',
            type=int,
            default=10,
            help='Number of test fields to create'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_fields = options['fields']
        
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Create test users
        users = []
        for i in range(num_users):
            username = f'farmer{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='TestFarmer@2026',
                    first_name=f'Farmer',
                    last_name=f'{i+1}'
                )
                users.append(user)
                self.stdout.write(f'  Created user: {username}')
            else:
                users.append(User.objects.get(username=username))
        
        # Sample crop types
        crop_types = ['Wheat', 'Rice', 'Maize', 'Cotton', 'Sugarcane', 'Tomato']
        
        # Sample field names
        field_names = [
            'North Field', 'South Field', 'East Field', 'West Field',
            'Upper Plot', 'Lower Plot', 'Main Farm', 'Back Farm'
        ]
        
        # Create test fields
        fields_created = 0
        for i in range(num_fields):
            user = random.choice(users)
            crop_type = random.choice(crop_types)
            field_name = random.choice(field_names)
            
            # Create a simple rectangular polygon (longitude, latitude)
            base_lon = 77.5 + random.uniform(-0.5, 0.5)
            base_lat = 28.5 + random.uniform(-0.5, 0.5)
            offset = 0.01
            
            polygon = {
                "type": "Polygon",
                "coordinates": [[
                    [base_lon, base_lat],
                    [base_lon + offset, base_lat],
                    [base_lon + offset, base_lat + offset],
                    [base_lon, base_lat + offset],
                    [base_lon, base_lat]
                ]]
            }
            
            field = FieldData.objects.create(
                user=user,
                name=f'{field_name} {i+1}',
                cropType=crop_type,
                polygon=polygon
            )
            fields_created += 1
            
            # Create some field logs for this field
            activities = ['Watering', 'Fertilizer', 'Sowing', 'Pesticide', 'Harvest', 'Other']
            for j in range(random.randint(2, 5)):
                days_ago = random.randint(1, 30)
                FieldLog.objects.create(
                    field=field,
                    activity=random.choice(activities),
                    notes=f'Sample log entry {j+1}',
                    created_at=datetime.now() - timedelta(days=days_ago)
                )
        
        self.stdout.write(self.style.SUCCESS(f'\nSeeding complete!'))
        self.stdout.write(f'  Users created: {len(users)}')
        self.stdout.write(f'  Fields created: {fields_created}')
        self.stdout.write(f'  Field logs created: ~{fields_created * 3}')
        self.stdout.write(self.style.SUCCESS('\nTest credentials:'))
        self.stdout.write('  Username: farmer1, farmer2, etc.')
        self.stdout.write('  Password: TestFarmer@2026')

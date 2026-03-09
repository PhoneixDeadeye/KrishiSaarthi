"""
Django management command to seed government schemes into the database.
Usage: python manage.py seed_schemes [--force]

Replaces the runtime auto-seed in SchemesView to avoid race conditions
and ensure idempotent, auditable data loading.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from finance.models import GovernmentScheme


SAMPLE_SCHEMES = [
    {
        'name': 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
        'scheme_type': 'subsidy',
        'description': 'Direct income support of \u20b96,000 per year to farmer families.',
        'benefits': '\u20b96,000 per year in 3 equal installments of \u20b92,000 each.',
        'eligible_crops': [],
        'eligible_states': [],
        'min_land_acres': 0,
        'max_subsidy_amount': 6000,
        'documents_required': ['Aadhaar Card', 'Land Records', 'Bank Account'],
        'link': 'https://pmkisan.gov.in/',
        'is_active': True,
    },
    {
        'name': 'PMFBY (Pradhan Mantri Fasal Bima Yojana)',
        'scheme_type': 'insurance',
        'description': 'Crop insurance scheme to provide financial support in case of crop failure.',
        'benefits': 'Insurance coverage for crop damage due to natural calamities, pests, and diseases.',
        'eligible_crops': ['Rice', 'Wheat', 'Cotton', 'Maize', 'Sugarcane', 'Pulses', 'Oilseeds'],
        'eligible_states': [],
        'min_land_acres': 0,
        'max_subsidy_amount': None,
        'subsidy_percentage': 50,
        'documents_required': ['Aadhaar Card', 'Land Records', 'Bank Account', 'Sowing Certificate'],
        'link': 'https://pmfby.gov.in/',
        'is_active': True,
    },
    {
        'name': 'KCC (Kisan Credit Card)',
        'scheme_type': 'loan',
        'description': 'Credit facility for farmers to meet their agricultural and other needs.',
        'benefits': 'Credit limit based on landholding. Interest rate at 4% p.a. for loans up to \u20b93 lakh.',
        'eligible_crops': [],
        'eligible_states': [],
        'min_land_acres': 0,
        'max_subsidy_amount': 300000,
        'documents_required': ['Aadhaar Card', 'Land Records', 'Passport Photo'],
        'link': 'https://www.nabard.org/content.aspx?id=497',
        'is_active': True,
    },
    {
        'name': 'Soil Health Card Scheme',
        'scheme_type': 'grant',
        'description': 'Free soil testing and recommendations for optimal fertilizer use.',
        'benefits': 'Free soil analysis and fertilizer recommendations. Reduces input costs by 10-15%.',
        'eligible_crops': [],
        'eligible_states': [],
        'min_land_acres': 0,
        'max_subsidy_amount': None,
        'documents_required': ['Aadhaar Card', 'Land Details'],
        'link': 'https://soilhealth.dac.gov.in/',
        'is_active': True,
    },
    {
        'name': 'Punjab Crop Diversification Scheme',
        'scheme_type': 'subsidy',
        'description': 'Incentive for farmers to shift from paddy to alternative crops.',
        'benefits': '\u20b97,500 per acre for shifting to maize, cotton, or pulses from paddy.',
        'eligible_crops': ['Maize', 'Cotton', 'Pulses'],
        'eligible_states': ['Punjab'],
        'min_land_acres': 1,
        'max_subsidy_amount': 37500,
        'documents_required': ['Aadhaar Card', 'Land Records', 'Crop Details'],
        'link': 'https://agri.punjab.gov.in/',
        'is_active': True,
        'application_deadline': (timezone.now() + timedelta(days=45)).date(),
    },
    {
        'name': 'Micro Irrigation Subsidy',
        'scheme_type': 'subsidy',
        'description': 'Subsidy for drip and sprinkler irrigation systems.',
        'benefits': 'Up to 55% subsidy on drip irrigation, 45% on sprinkler systems.',
        'eligible_crops': [],
        'eligible_states': [],
        'min_land_acres': 0.5,
        'subsidy_percentage': 55,
        'documents_required': ['Aadhaar Card', 'Land Records', 'Quotation from Vendor'],
        'link': 'https://pmksy.gov.in/',
        'is_active': True,
    },
    {
        'name': 'Organic Farming Certification',
        'scheme_type': 'grant',
        'description': 'Support for organic farming certification and inputs.',
        'benefits': '\u20b950,000 per hectare over 3 years for certification and inputs.',
        'eligible_crops': [],
        'eligible_states': [],
        'min_land_acres': 1,
        'max_subsidy_amount': 50000,
        'documents_required': ['Aadhaar Card', 'Land Records', 'No Chemical Use Declaration'],
        'link': 'https://pgsindia-ncof.gov.in/',
        'is_active': True,
    },
]


class Command(BaseCommand):
    help = 'Seeds government schemes into the database (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete existing schemes and re-seed from scratch.',
        )

    def handle(self, *args, **options):
        if options['force']:
            deleted, _ = GovernmentScheme.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing schemes.'))

        if GovernmentScheme.objects.exists():
            self.stdout.write(self.style.SUCCESS('Schemes already seeded. Use --force to re-seed.'))
            return

        created = 0
        for data in SAMPLE_SCHEMES:
            GovernmentScheme.objects.create(
                name=data['name'],
                scheme_type=data['scheme_type'],
                description=data['description'],
                benefits=data.get('benefits', ''),
                eligible_crops=data.get('eligible_crops', []),
                eligible_states=data.get('eligible_states', []),
                min_land_acres=data.get('min_land_acres', 0),
                max_subsidy_amount=data.get('max_subsidy_amount'),
                subsidy_percentage=data.get('subsidy_percentage'),
                documents_required=data.get('documents_required', []),
                link=data.get('link', ''),
                is_active=data.get('is_active', True),
                application_deadline=data.get('application_deadline'),
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created} government schemes.'))

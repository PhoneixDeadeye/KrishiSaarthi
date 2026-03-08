"""
Government Schemes view for KrishiSaarthi.
Matches farmers with eligible government schemes based on their profile.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

from ..models import GovernmentScheme
from field.models import FieldData

logger = logging.getLogger(__name__)


# Sample schemes data (in production, this would come from the database)
SAMPLE_SCHEMES = [
    {
        'id': 1,
        'name': 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
        'scheme_type': 'subsidy',
        'description': 'Direct income support of ₹6,000 per year to farmer families.',
        'benefits': '₹6,000 per year in 3 equal installments of ₹2,000 each.',
        'eligible_crops': [],  # All crops
        'eligible_states': [],  # All states
        'min_land_acres': 0,
        'max_subsidy_amount': 6000,
        'documents_required': ['Aadhaar Card', 'Land Records', 'Bank Account'],
        'link': 'https://pmkisan.gov.in/',
        'is_active': True,
    },
    {
        'id': 2,
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
        'id': 3,
        'name': 'KCC (Kisan Credit Card)',
        'scheme_type': 'loan',
        'description': 'Credit facility for farmers to meet their agricultural and other needs.',
        'benefits': 'Credit limit based on landholding. Interest rate at 4% p.a. for loans up to ₹3 lakh.',
        'eligible_crops': [],
        'eligible_states': [],
        'min_land_acres': 0,
        'max_subsidy_amount': 300000,
        'documents_required': ['Aadhaar Card', 'Land Records', 'Passport Photo'],
        'link': 'https://www.nabard.org/content.aspx?id=497',
        'is_active': True,
    },
    {
        'id': 4,
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
        'id': 5,
        'name': 'Punjab Crop Diversification Scheme',
        'scheme_type': 'subsidy',
        'description': 'Incentive for farmers to shift from paddy to alternative crops.',
        'benefits': '₹7,500 per acre for shifting to maize, cotton, or pulses from paddy.',
        'eligible_crops': ['Maize', 'Cotton', 'Pulses'],
        'eligible_states': ['Punjab'],
        'min_land_acres': 1,
        'max_subsidy_amount': 37500,  # 5 acres max
        'documents_required': ['Aadhaar Card', 'Land Records', 'Crop Details'],
        'link': 'https://agri.punjab.gov.in/',
        'is_active': True,
        'application_deadline': (timezone.now() + timedelta(days=45)).date().isoformat(),
    },
    {
        'id': 6,
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
        'id': 7,
        'name': 'Organic Farming Certification',
        'scheme_type': 'grant',
        'description': 'Support for organic farming certification and inputs.',
        'benefits': '₹50,000 per hectare over 3 years for certification and inputs.',
        'eligible_crops': [],
        'eligible_states': [],
        'min_land_acres': 1,
        'max_subsidy_amount': 50000,
        'documents_required': ['Aadhaar Card', 'Land Records', 'No Chemical Use Declaration'],
        'link': 'https://pgsindia-ncof.gov.in/',
        'is_active': True,
    },
]


class SchemesView(APIView):
    """
    GET: Returns eligible government schemes for the farmer.
    Queries from the GovernmentScheme database table.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state = request.query_params.get('state', None)
        crop = request.query_params.get('crop', None)
        scheme_type = request.query_params.get('type', None)
        land_acres = request.query_params.get('land_acres', None)

        # Auto-seed DB with sample data on first access if empty
        if not GovernmentScheme.objects.exists():
            self._seed_schemes()

        # Build queryset
        qs = GovernmentScheme.objects.filter(is_active=True)

        if scheme_type:
            qs = qs.filter(scheme_type=scheme_type)

        # Use values_list to avoid loading full model instances (N+1 fix)
        user_crops = list(
            FieldData.objects.filter(user=request.user)
            .exclude(cropType='')
            .values_list('cropType', flat=True)
            .distinct()
        )

        if land_acres:
            try:
                land_acres_float = float(land_acres)
                qs = qs.filter(min_land_acres__lte=land_acres_float)
            except (ValueError, TypeError):
                pass

        # Apply state/crop filters in Python because JSONField __contains
        # is not supported on SQLite. On PostgreSQL the DB-level filter
        # would be more efficient, but this keeps the code DB-agnostic.
        eligible_schemes = []
        for scheme in qs:
            # Filter by state (Python-side for SQLite compatibility)
            if state and scheme.eligible_states and state not in scheme.eligible_states:
                continue
            # Filter by crop
            if crop and scheme.eligible_crops and crop not in scheme.eligible_crops:
                continue

            scheme_data = {
                'id': scheme.id,
                'name': scheme.name,
                'scheme_type': scheme.scheme_type,
                'description': scheme.description,
                'benefits': scheme.benefits,
                'eligible_crops': scheme.eligible_crops,
                'eligible_states': scheme.eligible_states,
                'min_land_acres': float(scheme.min_land_acres),
                'max_subsidy_amount': float(scheme.max_subsidy_amount) if scheme.max_subsidy_amount else None,
                'subsidy_percentage': scheme.subsidy_percentage,
                'documents_required': scheme.documents_required,
                'link': scheme.link,
                'is_active': scheme.is_active,
                'application_deadline': scheme.application_deadline.isoformat() if scheme.application_deadline else None,
            }

            match_score = self._calculate_match_score(scheme_data, user_crops, state)
            scheme_data['match_score'] = match_score
            eligible_schemes.append(scheme_data)

        eligible_schemes.sort(key=lambda x: x['match_score'], reverse=True)

        grouped = {
            'subsidy': [], 'loan': [], 'insurance': [], 'grant': [], 'training': [],
        }
        for s in eligible_schemes:
            key = s['scheme_type']
            if key in grouped:
                grouped[key].append(s)

        return Response({
            'total_schemes': len(eligible_schemes),
            'user_crops': user_crops,
            'schemes': eligible_schemes,
            'grouped': grouped,
            'tips': [
                {'icon': '📅', 'text': 'Check application deadlines. Apply at least 2 weeks before the deadline.'},
                {'icon': '📄', 'text': 'Keep digital copies of all documents ready. Most schemes now accept online applications.'},
                {'icon': '🏦', 'text': 'Ensure your bank account is linked to Aadhaar for direct benefit transfers.'},
            ]
        })

    def _calculate_match_score(self, scheme, user_crops, state):
        """Calculate how well a scheme matches the user's profile"""
        score = 50

        if scheme['eligible_crops']:
            matching_crops = set(user_crops) & set(scheme['eligible_crops'])
            if matching_crops:
                score += 30
        else:
            score += 20

        if scheme['eligible_states']:
            if state in scheme['eligible_states']:
                score += 20
        else:
            score += 10

        if scheme.get('application_deadline'):
            score += 10

        return min(100, score)

    def _seed_schemes(self):
        """Seed the database with initial government scheme data."""
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
            )
        logger.info(f"Seeded {len(SAMPLE_SCHEMES)} government schemes into DB")


class SchemeDetailView(APIView):
    """
    GET: Returns details of a specific scheme from DB
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, scheme_id):
        scheme = get_object_or_404(GovernmentScheme, id=scheme_id)

        return Response({
            'id': scheme.id,
            'name': scheme.name,
            'scheme_type': scheme.scheme_type,
            'description': scheme.description,
            'benefits': scheme.benefits,
            'eligible_crops': scheme.eligible_crops,
            'eligible_states': scheme.eligible_states,
            'min_land_acres': float(scheme.min_land_acres),
            'max_land_acres': float(scheme.max_land_acres) if scheme.max_land_acres else None,
            'max_subsidy_amount': float(scheme.max_subsidy_amount) if scheme.max_subsidy_amount else None,
            'subsidy_percentage': scheme.subsidy_percentage,
            'application_deadline': scheme.application_deadline.isoformat() if scheme.application_deadline else None,
            'valid_from': scheme.valid_from.isoformat() if scheme.valid_from else None,
            'valid_until': scheme.valid_until.isoformat() if scheme.valid_until else None,
            'documents_required': scheme.documents_required,
            'link': scheme.link,
            'is_active': scheme.is_active,
        })

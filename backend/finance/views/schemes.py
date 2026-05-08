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
from ..services.live_data import fetch_live_schemes

logger = logging.getLogger(__name__)


# Sample schemes data (in production, this would come from the database)
SAMPLE_SCHEMES = [
    {
        "id": 1,
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "scheme_type": "subsidy",
        "description": "Direct income support of ₹6,000 per year to farmer families.",
        "benefits": "₹6,000 per year in 3 equal installments of ₹2,000 each.",
        "eligible_crops": [],  # All crops
        "eligible_states": [],  # All states
        "min_land_acres": 0,
        "max_subsidy_amount": 6000,
        "documents_required": ["Aadhaar Card", "Land Records", "Bank Account"],
        "link": "https://pmkisan.gov.in/",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
        "scheme_type": "insurance",
        "description": "Crop insurance scheme to provide financial support in case of crop failure.",
        "benefits": "Insurance coverage for crop damage due to natural calamities, pests, and diseases.",
        "eligible_crops": [
            "Rice",
            "Wheat",
            "Cotton",
            "Maize",
            "Sugarcane",
            "Pulses",
            "Oilseeds",
        ],
        "eligible_states": [],
        "min_land_acres": 0,
        "max_subsidy_amount": None,
        "subsidy_percentage": 50,
        "documents_required": [
            "Aadhaar Card",
            "Land Records",
            "Bank Account",
            "Sowing Certificate",
        ],
        "link": "https://pmfby.gov.in/",
        "is_active": True,
    },
    {
        "id": 3,
        "name": "KCC (Kisan Credit Card)",
        "scheme_type": "loan",
        "description": "Credit facility for farmers to meet their agricultural and other needs.",
        "benefits": "Credit limit based on landholding. Interest rate at 4% p.a. for loans up to ₹3 lakh.",
        "eligible_crops": [],
        "eligible_states": [],
        "min_land_acres": 0,
        "max_subsidy_amount": 300000,
        "documents_required": ["Aadhaar Card", "Land Records", "Passport Photo"],
        "link": "https://www.nabard.org/content.aspx?id=497",
        "is_active": True,
    },
    {
        "id": 4,
        "name": "Soil Health Card Scheme",
        "scheme_type": "grant",
        "description": "Free soil testing and recommendations for optimal fertilizer use.",
        "benefits": "Free soil analysis and fertilizer recommendations. Reduces input costs by 10-15%.",
        "eligible_crops": [],
        "eligible_states": [],
        "min_land_acres": 0,
        "max_subsidy_amount": None,
        "documents_required": ["Aadhaar Card", "Land Details"],
        "link": "https://soilhealth.dac.gov.in/",
        "is_active": True,
    },
    {
        "id": 5,
        "name": "Punjab Crop Diversification Scheme",
        "scheme_type": "subsidy",
        "description": "Incentive for farmers to shift from paddy to alternative crops.",
        "benefits": "₹7,500 per acre for shifting to maize, cotton, or pulses from paddy.",
        "eligible_crops": ["Maize", "Cotton", "Pulses"],
        "eligible_states": ["Punjab"],
        "min_land_acres": 1,
        "max_subsidy_amount": 37500,  # 5 acres max
        "documents_required": ["Aadhaar Card", "Land Records", "Crop Details"],
        "link": "https://agri.punjab.gov.in/",
        "is_active": True,
        "application_deadline": (timezone.now() + timedelta(days=45))
        .date()
        .isoformat(),
    },
    {
        "id": 6,
        "name": "Micro Irrigation Subsidy",
        "scheme_type": "subsidy",
        "description": "Subsidy for drip and sprinkler irrigation systems.",
        "benefits": "Up to 55% subsidy on drip irrigation, 45% on sprinkler systems.",
        "eligible_crops": [],
        "eligible_states": [],
        "min_land_acres": 0.5,
        "subsidy_percentage": 55,
        "documents_required": ["Aadhaar Card", "Land Records", "Quotation from Vendor"],
        "link": "https://pmksy.gov.in/",
        "is_active": True,
    },
    {
        "id": 7,
        "name": "Organic Farming Certification",
        "scheme_type": "grant",
        "description": "Support for organic farming certification and inputs.",
        "benefits": "₹50,000 per hectare over 3 years for certification and inputs.",
        "eligible_crops": [],
        "eligible_states": [],
        "min_land_acres": 1,
        "max_subsidy_amount": 50000,
        "documents_required": [
            "Aadhaar Card",
            "Land Records",
            "No Chemical Use Declaration",
        ],
        "link": "https://pgsindia-ncof.gov.in/",
        "is_active": True,
    },
]


class SchemesView(APIView):
    """
    GET: Returns eligible government schemes for the farmer.
    Uses Gemini to fetch live, accurate scheme recommendations based on user profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        import os
        import json
        import re
        import google.generativeai as genai
        
        state = request.query_params.get("state", "India")
        crop = request.query_params.get("crop", "Any")
        scheme_type = request.query_params.get("type", "All")
        land_acres = request.query_params.get("land_acres", "Not specified")

        # Get user's actual crops if available
        user_crops = list(
            FieldData.objects.filter(user=request.user)
            .exclude(cropType="")
            .values_list("cropType", flat=True)
            .distinct()
        )
        if not crop or crop == "Any" and user_crops:
            crop = ", ".join(user_crops)

        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("No Gemini key configured")
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are an agriculture government scheme expert in India.
            Provide a realistic list of currently active agricultural government schemes in India.
            Limit to 4-5 highly relevant schemes.

            Filters: 
            State: {state}
            Crop: {crop}
            Scheme Type: {scheme_type}
            Land Size (Acres): {land_acres}

            Return exactly a JSON array of objects. Do not use block quotes, just the pure JSON.
            Each object must have these exactly properties:
            "id": number
            "name": string
            "scheme_type": string (one of "subsidy", "insurance", "loan", "grant")
            "description": string (1-2 sentences)
            "benefits": string
            "eligible_crops": array of strings
            "eligible_states": array of strings
            "min_land_acres": number
            "max_subsidy_amount": null or number
            "documents_required": array of strings
            "link": string (URL)
            """
            response = model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                ai_schemes = json.loads(match.group(0))
                
                # Group schemes
                grouped = {
                    "subsidy": [s for s in ai_schemes if s.get("scheme_type") == "subsidy"],
                    "loan": [s for s in ai_schemes if s.get("scheme_type") == "loan"],
                    "insurance": [s for s in ai_schemes if s.get("scheme_type") == "insurance"],
                    "grant": [s for s in ai_schemes if s.get("scheme_type") == "grant"],
                    "training": [s for s in ai_schemes if s.get("scheme_type") == "training"],
                }
                
                return Response(
                    {
                        "total_schemes": len(ai_schemes),
                        "user_crops": user_crops,
                        "schemes": ai_schemes,
                        "grouped": grouped,
                        "tips": [
                            "Apply for schemes before the pre-sowing season.",
                            "Keep your land records (Khasra/Khatauni) updated."
                        ],
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to fetch dynamic schemes: {e}")
            pass

        # Fallback to local static sample if API fails
        if not GovernmentScheme.objects.exists():
            return Response(
                {
                    "total_schemes": len(SAMPLE_SCHEMES),
                    "user_crops": user_crops,
                    "schemes": SAMPLE_SCHEMES,
                    "grouped": {
                        "subsidy": [s for s in SAMPLE_SCHEMES if s["scheme_type"] == "subsidy"],
                        "loan": [s for s in SAMPLE_SCHEMES if s["scheme_type"] == "loan"],
                        "insurance": [s for s in SAMPLE_SCHEMES if s["scheme_type"] == "insurance"],
                        "grant": [s for s in SAMPLE_SCHEMES if s["scheme_type"] == "grant"],
                        "training": [],
                    },
                    "tips": ["(Data running in static fallback mode. Ensure APIs are active.)"],
                }
            )

        # Build queryset from DB 
        qs = GovernmentScheme.objects.filter(is_active=True)

        if scheme_type and scheme_type != "All":
            qs = qs.filter(scheme_type=scheme_type)

        if land_acres and land_acres != "Not specified":
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
                "id": scheme.id,
                "name": scheme.name,
                "scheme_type": scheme.scheme_type,
                "description": scheme.description,
                "benefits": scheme.benefits,
                "eligible_crops": scheme.eligible_crops,
                "eligible_states": scheme.eligible_states,
                "min_land_acres": float(scheme.min_land_acres),
                "max_subsidy_amount": (
                    float(scheme.max_subsidy_amount)
                    if scheme.max_subsidy_amount
                    else None
                ),
                "subsidy_percentage": scheme.subsidy_percentage,
                "documents_required": scheme.documents_required,
                "link": scheme.link,
                "is_active": scheme.is_active,
                "application_deadline": (
                    scheme.application_deadline.isoformat()
                    if scheme.application_deadline
                    else None
                ),
            }

            match_score = self._calculate_match_score(scheme_data, user_crops, state)
            scheme_data["match_score"] = match_score
            eligible_schemes.append(scheme_data)

        eligible_schemes.sort(key=lambda x: x["match_score"], reverse=True)

        grouped = {
            "subsidy": [],
            "loan": [],
            "insurance": [],
            "grant": [],
            "training": [],
        }
        for s in eligible_schemes:
            key = s["scheme_type"]
            if key in grouped:
                grouped[key].append(s)

        return Response(
            {
                "total_schemes": len(eligible_schemes),
                "user_crops": user_crops,
                "schemes": eligible_schemes,
                "grouped": grouped,
                "live_schemes_news": fetch_live_schemes(crop, state),
                "tips": [
                    {
                        "icon": "📅",
                        "text": "Check application deadlines. Apply at least 2 weeks before the deadline.",
                    },
                    {
                        "icon": "📄",
                        "text": "Keep digital copies of all documents ready. Most schemes now accept online applications.",
                    },
                    {
                        "icon": "🏦",
                        "text": "Ensure your bank account is linked to Aadhaar for direct benefit transfers.",
                    },
                ],
            }
        )

    def _calculate_match_score(self, scheme, user_crops, state):
        """Calculate how well a scheme matches the user's profile"""
        score = 50

        if scheme["eligible_crops"]:
            matching_crops = set(user_crops) & set(scheme["eligible_crops"])
            if matching_crops:
                score += 30
        else:
            score += 20

        if scheme["eligible_states"]:
            if state in scheme["eligible_states"]:
                score += 20
        else:
            score += 10

        if scheme.get("application_deadline"):
            score += 10

        return min(100, score)

    def _seed_schemes(self):
        """Seed the database with initial government scheme data."""
        for data in SAMPLE_SCHEMES:
            GovernmentScheme.objects.create(
                name=data["name"],
                scheme_type=data["scheme_type"],
                description=data["description"],
                benefits=data.get("benefits", ""),
                eligible_crops=data.get("eligible_crops", []),
                eligible_states=data.get("eligible_states", []),
                min_land_acres=data.get("min_land_acres", 0),
                max_subsidy_amount=data.get("max_subsidy_amount"),
                subsidy_percentage=data.get("subsidy_percentage"),
                documents_required=data.get("documents_required", []),
                link=data.get("link", ""),
                is_active=data.get("is_active", True),
            )
        logger.info("Seeded %d government schemes into DB", len(SAMPLE_SCHEMES))


class SchemeDetailView(APIView):
    """
    GET: Returns details of a specific scheme from DB
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        scheme = get_object_or_404(GovernmentScheme, id=pk)

        return Response(
            {
                "id": scheme.id,
                "name": scheme.name,
                "scheme_type": scheme.scheme_type,
                "description": scheme.description,
                "benefits": scheme.benefits,
                "eligible_crops": scheme.eligible_crops,
                "eligible_states": scheme.eligible_states,
                "min_land_acres": float(scheme.min_land_acres),
                "max_land_acres": (
                    float(scheme.max_land_acres) if scheme.max_land_acres else None
                ),
                "max_subsidy_amount": (
                    float(scheme.max_subsidy_amount)
                    if scheme.max_subsidy_amount
                    else None
                ),
                "subsidy_percentage": scheme.subsidy_percentage,
                "application_deadline": (
                    scheme.application_deadline.isoformat()
                    if scheme.application_deadline
                    else None
                ),
                "valid_from": (
                    scheme.valid_from.isoformat() if scheme.valid_from else None
                ),
                "valid_until": (
                    scheme.valid_until.isoformat() if scheme.valid_until else None
                ),
                "documents_required": scheme.documents_required,
                "link": scheme.link,
                "is_active": scheme.is_active,
            }
        )

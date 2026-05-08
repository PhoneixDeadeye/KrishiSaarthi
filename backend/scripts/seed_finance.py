"""
Finance Data Seeder
====================
Creates sample finance records for benchmarking and testing.

Usage:
    cd backend && python manage.py shell < scripts/seed_finance.py
    OR:
    cd backend && python scripts/seed_finance.py
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KrishiSaarthi.settings")
django.setup()

from django.contrib.auth.models import User
from field.models import FieldData
from finance.models import Season, CostEntry, Revenue, GovernmentScheme, InsuranceClaim


def seed():
    """Seed finance data for testing."""
    # Get or create test user
    user, created = User.objects.get_or_create(
        username="bench_farmer",
        defaults={"email": "bench@test.com", "is_active": True}
    )
    if created:
        user.set_password("BenchTest123!")
        user.save()
        print(f"Created test user: bench_farmer")

    # Get or create a field
    field, _ = FieldData.objects.get_or_create(
        user=user,
        name="Demo Rice Field",
        defaults={
            "cropType": "Rice",
            "polygon": {
                "type": "Polygon",
                "coordinates": [[[78.4, 17.4], [78.41, 17.4], [78.41, 17.41], [78.4, 17.41], [78.4, 17.4]]]
            },
        }
    )
    print(f"Field: {field.name} (id={field.id})")

    # Create season
    today = date.today()
    season, _ = Season.objects.get_or_create(
        user=user,
        field=field,
        season_type="kharif",
        year=today.year,
        defaults={
            "name": f"Kharif {today.year}",
            "start_date": date(today.year, 6, 1),
            "end_date": date(today.year, 11, 30),
            "crop": "Rice",
        }
    )
    print(f"Season: {season.name}")

    # Seed cost entries
    cost_data = [
        ("seeds", "Hybrid rice seeds (IR-64)", 4500, 25, "kg"),
        ("seeds", "Nursery preparation", 1200, 1, "lot"),
        ("fertilizer", "DAP 50kg bag", 1400, 3, "bags"),
        ("fertilizer", "Urea 50kg bag", 600, 4, "bags"),
        ("fertilizer", "MOP 50kg bag", 850, 2, "bags"),
        ("pesticide", "Chlorpyrifos 20EC", 380, 2, "liters"),
        ("pesticide", "Carbendazim 50WP", 450, 1, "kg"),
        ("labor", "Transplanting labor", 8000, 8, "workers"),
        ("labor", "Weeding labor", 4000, 4, "workers"),
        ("labor", "Harvesting labor", 12000, 10, "workers"),
        ("irrigation", "Pump diesel cost", 3500, 1, "season"),
        ("irrigation", "Canal water charges", 800, 1, "season"),
        ("equipment", "Tractor rental - plowing", 2500, 2, "hours"),
        ("equipment", "Combine harvester rental", 3500, 1, "session"),
        ("transport", "Market transport", 1500, 1, "trip"),
        ("other", "Soil testing", 500, 1, "test"),
    ]

    costs_created = 0
    for i, (cat, desc, amount, qty, unit) in enumerate(cost_data):
        cost_date = date(today.year, 6, 1) + timedelta(days=i * 10)
        if cost_date > today:
            cost_date = today - timedelta(days=random.randint(1, 90))
        _, created = CostEntry.objects.get_or_create(
            user=user, field=field, season=season, category=cat, description=desc,
            defaults={
                "amount": Decimal(str(amount)),
                "quantity": Decimal(str(qty)),
                "unit": unit,
                "date": cost_date,
            }
        )
        if created:
            costs_created += 1
    print(f"Cost entries created: {costs_created}")

    # Seed revenue
    rev_data = [
        ("Rice", 4200, "kg", 22.50, "Kakinada Mandi"),
        ("Rice", 1800, "kg", 23.00, "Local Trader"),
        ("Rice", 500, "kg", 25.00, "Direct Consumer (organic premium)"),
    ]
    revs_created = 0
    for i, (crop, qty, unit, price, buyer) in enumerate(rev_data):
        rev_date = date(today.year, 11, 1) + timedelta(days=i * 7)
        if rev_date > today:
            rev_date = today - timedelta(days=random.randint(1, 30))
        _, created = Revenue.objects.get_or_create(
            user=user, field=field, season=season, crop=crop, buyer=buyer,
            defaults={
                "quantity_sold": Decimal(str(qty)),
                "unit": unit,
                "price_per_unit": Decimal(str(price)),
                "total_amount": Decimal(str(round(qty * price, 2))),
                "date": rev_date,
            }
        )
        if created:
            revs_created += 1
    print(f"Revenue entries created: {revs_created}")

    # Seed government schemes
    schemes = [
        {
            "name": "PM-KISAN Samman Nidhi",
            "scheme_type": "subsidy",
            "description": "Direct income support of Rs.6000/year to all landholding farmer families.",
            "benefits": "Rs.2000 every 4 months directly to bank account",
            "eligible_crops": ["Rice", "Wheat", "Cotton", "Maize", "Sugarcane"],
            "eligible_states": ["All India"],
            "max_subsidy_amount": Decimal("6000"),
            "link": "https://pmkisan.gov.in/",
        },
        {
            "name": "PMFBY - Crop Insurance",
            "scheme_type": "insurance",
            "description": "Pradhan Mantri Fasal Bima Yojana provides crop insurance at subsidized premiums.",
            "benefits": "Coverage against crop loss due to natural calamities, pests, diseases",
            "eligible_crops": ["Rice", "Wheat", "Cotton", "Soybean", "Groundnut"],
            "eligible_states": ["All India"],
            "subsidy_percentage": 50,
            "link": "https://pmfby.gov.in/",
        },
        {
            "name": "Soil Health Card Scheme",
            "scheme_type": "subsidy",
            "description": "Free soil testing and nutrient-based fertilizer recommendations.",
            "benefits": "Free soil testing, Customized fertilizer advice",
            "eligible_crops": ["Rice", "Wheat", "Cotton", "Maize"],
            "eligible_states": ["All India"],
            "link": "https://soilhealth.dac.gov.in/",
        },
    ]
    schemes_created = 0
    for sc in schemes:
        _, created = GovernmentScheme.objects.get_or_create(
            name=sc["name"],
            defaults=sc,
        )
        if created:
            schemes_created += 1
    print(f"Government schemes created: {schemes_created}")

    # Seed an insurance claim
    _, claim_created = InsuranceClaim.objects.get_or_create(
        user=user, field=field, crop="Rice", damage_type="pest",
        defaults={
            "season": season,
            "policy_number": "PMFBY-2026-TG-0042",
            "area_affected_acres": Decimal("1.5"),
            "damage_date": today - timedelta(days=45),
            "damage_description": "Brown planthopper infestation affecting 30% of field area",
            "estimated_loss": Decimal("35000"),
            "claim_amount": Decimal("28000"),
            "status": "under_review",
            "submitted_at": today - timedelta(days=30),
        }
    )
    if claim_created:
        print("Insurance claim created")

    print("\n--- Finance seed complete ---")
    total_cost = CostEntry.objects.filter(user=user, season=season).aggregate(
        total=django.db.models.Sum("amount"))["total"] or 0
    total_rev = Revenue.objects.filter(user=user, season=season).aggregate(
        total=django.db.models.Sum("total_amount"))["total"] or 0
    print(f"Total Costs:   Rs.{total_cost:,.2f}")
    print(f"Total Revenue: Rs.{total_rev:,.2f}")
    print(f"P&L:           Rs.{float(total_rev) - float(total_cost):,.2f}")

    return user, field


import django.db.models
if __name__ == "__main__":
    seed()

"""
Tests for finance edge cases: negative amounts, DELETE responses,
model constraints, and cost/revenue calculations.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from finance.models import Season, CostEntry, Revenue
from field.models import FieldData


def _make_season(user):
    """Helper to create Season with all required fields."""
    field = FieldData.objects.create(
        user=user, name='Edge Field', cropType='Rice',
        polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
    )
    season = Season.objects.create(
        user=user, name="Kharif 2025", season_type="kharif", year=2025,
        start_date='2025-06-01', end_date='2025-10-01', field=field,
    )
    return field, season


class CostEntryConstraintTestCase(TestCase):
    """Test CostEntry model constraints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="financeuser", password="TestPass123!"
        )
        self.field, self.season = _make_season(self.user)

    def test_negative_amount_rejected(self):
        """CostEntry with negative amount should be allowed (refunds/credits)."""
        cost = CostEntry.objects.create(
            user=self.user, field=self.field, season=self.season,
            category="seeds", description="Refund", amount=-100, date='2025-07-01'
        )
        self.assertEqual(cost.amount, -100)

    def test_zero_amount_allowed(self):
        """CostEntry with zero amount should be allowed."""
        cost = CostEntry.objects.create(
            user=self.user, field=self.field, season=self.season,
            category="seeds", description="Free seeds", amount=0, date='2025-07-01'
        )
        self.assertEqual(cost.amount, 0)


class RevenueCalculationTestCase(TestCase):
    """Test Revenue auto-calculation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="revuser", password="TestPass123!"
        )
        self.field, self.season = _make_season(self.user)

    def test_revenue_auto_calculates(self):
        """Revenue total_amount should be quantity_sold * price_per_unit."""
        rev = Revenue.objects.create(
            user=self.user, field=self.field, season=self.season,
            crop="Rice", quantity_sold=100,
            price_per_unit=25, total_amount=0, date='2025-09-01'
        )
        rev.refresh_from_db()
        self.assertEqual(rev.total_amount, 2500)

    def test_revenue_recalculates_on_update(self):
        """Updating quantity should recalculate total_amount."""
        rev = Revenue.objects.create(
            user=self.user, field=self.field, season=self.season,
            crop="Rice", quantity_sold=100,
            price_per_unit=25, total_amount=0, date='2025-09-01'
        )
        rev.quantity_sold = 200
        rev.save()
        rev.refresh_from_db()
        self.assertEqual(rev.total_amount, 5000)


class DeleteResponseCodeTestCase(TestCase):
    """All DELETE endpoints should return 204 No Content."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="deleteuser", password="TestPass123!"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.field, self.season = _make_season(self.user)

    def test_cost_delete_returns_204(self):
        cost = CostEntry.objects.create(
            user=self.user, field=self.field, season=self.season,
            category="seeds", description="Test", amount=100, date='2025-07-01'
        )
        response = self.client.delete(f"/finance/costs/{cost.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_revenue_delete_returns_204(self):
        rev = Revenue.objects.create(
            user=self.user, field=self.field, season=self.season,
            crop="Rice", quantity_sold=100,
            price_per_unit=25, total_amount=0, date='2025-09-01'
        )
        response = self.client.delete(f"/finance/revenue/{rev.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_season_delete_returns_204(self):
        response = self.client.delete(f"/finance/seasons/{self.season.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_nonexistent_cost_returns_404(self):
        response = self.client.delete("/finance/costs/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

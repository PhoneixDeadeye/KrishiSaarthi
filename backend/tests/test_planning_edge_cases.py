"""
Tests for planning module edge cases: equipment booking overlaps,
inventory stock checks, labor wage calculations.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from field.models import FieldData
from planning.models import (
    Equipment, EquipmentBooking, InventoryItem,
    InventoryTransaction, LaborEntry
)


def _make_field(user):
    return FieldData.objects.create(
        user=user, name='Plan Field', cropType='Rice',
        polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
    )


class EquipmentBookingOverlapTestCase(TestCase):
    """Test equipment booking overlap validation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="equipuser", password="TestPass123!"
        )
        self.field = _make_field(self.user)
        self.equipment = Equipment.objects.create(
            user=self.user, name="Tractor",
            equipment_type="tractor", status="available"
        )
        now = timezone.now()
        self.booking = EquipmentBooking.objects.create(
            equipment=self.equipment, field=self.field, purpose="Plowing",
            start_datetime=now + timedelta(hours=1),
            end_datetime=now + timedelta(hours=3)
        )

    def test_overlapping_booking_rejected(self):
        """Booking that overlaps with existing should raise ValidationError."""
        now = timezone.now()
        overlapping = EquipmentBooking(
            equipment=self.equipment, field=self.field, purpose="Harvesting",
            start_datetime=now + timedelta(hours=2),
            end_datetime=now + timedelta(hours=4)
        )
        with self.assertRaises(ValidationError):
            overlapping.clean()

    def test_non_overlapping_booking_allowed(self):
        """Booking that doesn't overlap should be fine."""
        now = timezone.now()
        non_overlapping = EquipmentBooking(
            equipment=self.equipment, field=self.field, purpose="Transport",
            start_datetime=now + timedelta(hours=4),
            end_datetime=now + timedelta(hours=6)
        )
        # Should not raise
        non_overlapping.clean()
        non_overlapping.save()

    def test_end_before_start_rejected(self):
        """Booking where end < start should fail validation."""
        now = timezone.now()
        bad_booking = EquipmentBooking(
            equipment=self.equipment, field=self.field, purpose="Bad",
            start_datetime=now + timedelta(hours=5),
            end_datetime=now + timedelta(hours=3)
        )
        with self.assertRaises(ValidationError):
            bad_booking.clean()


class InventoryStockCheckTestCase(TestCase):
    """Test inventory stock check on transactions."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="invuser", password="TestPass123!"
        )
        self.item = InventoryItem.objects.create(
            user=self.user, name="Fertilizer",
            category="fertilizer", quantity=100,
            unit="kg"
        )

    def test_valid_deduction(self):
        """Deducting available stock should work."""
        txn = InventoryTransaction(
            item=self.item, transaction_type="use",
            quantity=50, notes="Used for field A",
            date=date.today(),
        )
        txn.save()
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 50)

    def test_overdraft_rejected(self):
        """Deducting more than available stock should raise ValidationError."""
        txn = InventoryTransaction(
            item=self.item, transaction_type="use",
            quantity=150, notes="Too much",
            date=date.today(),
        )
        with self.assertRaises(ValidationError):
            txn.save()

    def test_addition_always_works(self):
        """Adding stock should always work regardless of current quantity."""
        txn = InventoryTransaction(
            item=self.item, transaction_type="purchase",
            quantity=200, notes="Restocked",
            date=date.today(),
        )
        txn.save()
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 300)


class LaborWageCalculationTestCase(TestCase):
    """Test labor entry auto-calculation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="laboruser", password="TestPass123!"
        )
        self.field = _make_field(self.user)

    def test_total_wage_calculated(self):
        """Total wage should be hours_worked * hourly_rate."""
        entry = LaborEntry.objects.create(
            user=self.user, field=self.field, worker_name="Ram",
            work_type="Planting", hours_worked=8,
            hourly_rate=100, total_wage=0, date=date.today(),
        )
        self.assertEqual(entry.total_wage, 800)

    def test_total_wage_recalculated_on_update(self):
        """Updating hours should recalculate total_wage."""
        entry = LaborEntry.objects.create(
            user=self.user, field=self.field, worker_name="Ram",
            work_type="Planting", hours_worked=8,
            hourly_rate=100, total_wage=0, date=date.today(),
        )
        entry.hours_worked = 10
        entry.save()
        entry.refresh_from_db()
        self.assertEqual(entry.total_wage, 1000)


class PlanningDeleteEndpointTestCase(TestCase):
    """All planning DELETE endpoints should return 204."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="plandeluser", password="TestPass123!"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_equipment_delete_returns_204(self):
        equip = Equipment.objects.create(
            user=self.user, name="Spray",
            equipment_type="sprayer", status="available"
        )
        response = self.client.delete(f"/planning/equipment/{equip.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_nonexistent_equipment_returns_404(self):
        response = self.client.delete("/planning/equipment/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

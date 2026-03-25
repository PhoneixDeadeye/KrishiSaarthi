"""
Tests for the InsuranceClaim serializer and view refactoring.
"""
import pytest
from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from field.models import FieldData
from finance.models import InsuranceClaim
from finance.serializers import InsuranceClaimSerializer


@pytest.mark.django_db
class TestInsuranceClaimSerializer(TestCase):
    """Tests for InsuranceClaimSerializer validation."""

    def setUp(self):
        self.user = User.objects.create_user(username='testfarmer', password='testpass123')
        self.field = FieldData.objects.create(user=self.user, name='Test Field')

    def test_valid_claim_data(self):
        data = {
            'field': self.field.id,
            'crop': 'Rice',
            'damage_type': 'flood',
            'damage_date': '2026-01-15',
            'damage_description': 'Flood damaged 50% of crop',
            'area_affected_acres': 5.0,
            'estimated_loss': 50000,
        }
        serializer = InsuranceClaimSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_invalid_area_zero(self):
        data = {
            'field': self.field.id,
            'crop': 'Wheat',
            'damage_type': 'drought',
            'damage_date': '2026-02-01',
            'damage_description': 'Drought',
            'area_affected_acres': 0,
            'estimated_loss': 10000,
        }
        serializer = InsuranceClaimSerializer(data=data)
        assert not serializer.is_valid()
        assert 'area_affected_acres' in serializer.errors

    def test_invalid_estimated_loss_negative(self):
        data = {
            'field': self.field.id,
            'crop': 'Cotton',
            'damage_type': 'pest',
            'damage_date': '2026-03-01',
            'damage_description': 'Pest attack',
            'area_affected_acres': 2.0,
            'estimated_loss': -500,
        }
        serializer = InsuranceClaimSerializer(data=data)
        assert not serializer.is_valid()
        assert 'estimated_loss' in serializer.errors

    def test_invalid_ifsc_code_format(self):
        data = {
            'field': self.field.id,
            'crop': 'Rice',
            'damage_type': 'hail',
            'damage_date': '2026-01-20',
            'damage_description': 'Hail damage',
            'area_affected_acres': 3.0,
            'estimated_loss': 25000,
            'ifsc_code': 'INVALID',
        }
        serializer = InsuranceClaimSerializer(data=data)
        assert not serializer.is_valid()
        assert 'ifsc_code' in serializer.errors

    def test_valid_ifsc_code(self):
        data = {
            'field': self.field.id,
            'crop': 'Rice',
            'damage_type': 'fire',
            'damage_date': '2026-01-25',
            'damage_description': 'Fire damage',
            'area_affected_acres': 1.5,
            'estimated_loss': 15000,
            'ifsc_code': 'SBIN0001234',
        }
        serializer = InsuranceClaimSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_masked_bank_account(self):
        claim = InsuranceClaim.objects.create(
            user=self.user,
            field=self.field,
            crop='Rice',
            damage_type='flood',
            damage_date=date(2026, 1, 1),
            damage_description='Test',
            area_affected_acres=1,
            estimated_loss=10000,
            bank_account='1234567890',
        )
        serializer = InsuranceClaimSerializer(claim)
        masked = serializer.data['masked_bank_account']
        assert masked.endswith('7890')
        assert '●' in masked

    def test_field_id_alias_accepted(self):
        """Frontend sends field_id, serializer should accept it."""
        data = {
            'field_id': self.field.id,
            'crop': 'Rice',
            'damage_type': 'flood',
            'damage_date': '2026-01-15',
            'damage_description': 'Flood damage',
            'area_affected_acres': 5.0,
            'estimated_loss': 50000,
        }
        serializer = InsuranceClaimSerializer(data=data)
        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestInsuranceClaimAPI(TestCase):
    """Integration tests for insurance claim API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username='farmer1', password='testpass123')
        self.field = FieldData.objects.create(user=self.user, name='Paddy Field')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_claim_via_api(self):
        response = self.client.post('/finance/insurance/', {
            'field_id': self.field.id,
            'crop': 'Rice',
            'damage_type': 'flood',
            'damage_date': '2026-06-15',
            'damage_description': 'Monsoon flooding destroyed crops',
            'area_affected_acres': 3.5,
            'estimated_loss': 75000,
        }, format='json')
        assert response.status_code == 201
        assert 'claim_id' in response.data

    def test_create_claim_missing_field(self):
        response = self.client.post('/finance/insurance/', {
            'crop': 'Rice',
            'damage_type': 'flood',
            'damage_date': '2026-06-15',
            'damage_description': 'Test',
            'area_affected_acres': 1.0,
            'estimated_loss': 10000,
        }, format='json')
        assert response.status_code == 400

    def test_submit_draft_claim(self):
        claim = InsuranceClaim.objects.create(
            user=self.user,
            field=self.field,
            crop='Wheat',
            damage_type='drought',
            damage_date=date(2026, 3, 1),
            damage_description='Drought damage',
            area_affected_acres=2,
            estimated_loss=30000,
            status='draft',
        )
        response = self.client.patch(
            f'/finance/insurance/{claim.id}/',
            {'status': 'submitted'},
            format='json'
        )
        assert response.status_code == 200
        claim.refresh_from_db()
        assert claim.status == 'submitted'

    def test_delete_draft_claim(self):
        claim = InsuranceClaim.objects.create(
            user=self.user,
            field=self.field,
            crop='Cotton',
            damage_type='pest',
            damage_date=date(2026, 4, 1),
            damage_description='Pest attack',
            area_affected_acres=1,
            estimated_loss=5000,
            status='draft',
        )
        response = self.client.delete(f'/finance/insurance/{claim.id}/')
        assert response.status_code == 204

    def test_cannot_delete_submitted_claim(self):
        claim = InsuranceClaim.objects.create(
            user=self.user,
            field=self.field,
            crop='Rice',
            damage_type='hail',
            damage_date=date(2026, 5, 1),
            damage_description='Hailstorm',
            area_affected_acres=2,
            estimated_loss=20000,
            status='submitted',
        )
        response = self.client.delete(f'/finance/insurance/{claim.id}/')
        assert response.status_code == 400

    def test_list_claims(self):
        InsuranceClaim.objects.create(
            user=self.user,
            field=self.field,
            crop='Rice',
            damage_type='flood',
            damage_date=date(2026, 7, 1),
            damage_description='Flood',
            area_affected_acres=5,
            estimated_loss=100000,
        )
        response = self.client.get('/finance/insurance/')
        assert response.status_code == 200
        assert len(response.data['claims']) == 1

    def test_other_user_cannot_see_claims(self):
        """Claims are scoped to the owning user."""
        other_user = User.objects.create_user(username='other', password='pass123')
        InsuranceClaim.objects.create(
            user=self.user,
            field=self.field,
            crop='Rice',
            damage_type='flood',
            damage_date=date(2026, 7, 1),
            damage_description='Flood',
            area_affected_acres=5,
            estimated_loss=100000,
        )
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        response = other_client.get('/finance/insurance/')
        assert response.status_code == 200
        assert len(response.data['claims']) == 0

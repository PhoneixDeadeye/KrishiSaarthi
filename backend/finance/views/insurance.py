"""
Insurance Claims view for KrishiSaarthi.
Manages crop insurance claims under PMFBY.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
import logging
from config.pagination import get_optional_paginator

from ..models import InsuranceClaim, Season
from ..serializers import InsuranceClaimSerializer
from field.models import FieldData

logger = logging.getLogger(__name__)


class InsuranceClaimView(APIView):
    """
    GET: List user's insurance claims
    POST: Create new claim
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all claims for the user"""
        claims = InsuranceClaim.objects.filter(
            user=request.user
        ).select_related('field')
        
        # Filter by status if provided
        claim_status = request.query_params.get('status', None)
        if claim_status:
            claims = claims.filter(status=claim_status)

        paginator = get_optional_paginator(request)
        if paginator is not None:
            page = paginator.paginate_queryset(claims, request)
            claims_iterable = page
        else:
            claims_iterable = claims
        
        claims_data = []
        for claim in claims_iterable:
            claims_data.append({
                'id': claim.id,
                'field_id': claim.field_id,
                'field_name': claim.field.name if claim.field else None,
                'crop': claim.crop,
                'damage_type': claim.damage_type,
                'damage_type_display': claim.get_damage_type_display(),
                'damage_date': claim.damage_date.isoformat(),
                'area_affected_acres': float(claim.area_affected_acres),
                'estimated_loss': float(claim.estimated_loss),
                'claim_amount': float(claim.claim_amount) if claim.claim_amount else None,
                'status': claim.status,
                'status_display': claim.get_status_display(),
                'submitted_at': claim.submitted_at.isoformat() if claim.submitted_at else None,
                'created_at': claim.created_at.isoformat(),
            })
        
        # Get summary stats using DB-level aggregation (avoid N+1)
        total_claims = claims.count()
        pending_claims = claims.filter(status__in=['draft', 'submitted', 'under_review']).count()
        approved_total = claims.filter(
            status__in=['approved', 'paid']
        ).aggregate(
            total=Sum('claim_amount')
        )['total'] or 0
        
        payload = {
            'claims': claims_data,
            'summary': {
                'total_claims': total_claims,
                'pending_claims': pending_claims,
                'approved_total': approved_total,
            },
            'damage_types': [
                {'value': 'flood', 'label': 'Flood', 'icon': '🌊'},
                {'value': 'drought', 'label': 'Drought', 'icon': '☀️'},
                {'value': 'pest', 'label': 'Pest Attack', 'icon': '🐛'},
                {'value': 'disease', 'label': 'Crop Disease', 'icon': '🦠'},
                {'value': 'hail', 'label': 'Hailstorm', 'icon': '🌨️'},
                {'value': 'fire', 'label': 'Fire', 'icon': '🔥'},
                {'value': 'other', 'label': 'Other Natural Calamity', 'icon': '⚠️'},
            ],
            'tips': [
                {
                    'icon': '📸',
                    'text': 'Take photos of crop damage as soon as possible for evidence.',
                },
                {
                    'icon': '📞',
                    'text': 'Report crop loss within 72 hours to your local agriculture office.',
                },
                {
                    'icon': '📋',
                    'text': 'Keep your policy number and bank details ready when filing claims.',
                },
            ]
        }
        if paginator is not None:
            return paginator.get_paginated_response(payload)
        return Response(payload)
    
    def post(self, request):
        """Create a new insurance claim"""
        serializer = InsuranceClaimSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify field belongs to user
        field = get_object_or_404(FieldData, id=serializer.validated_data['field'].id, user=request.user)
        
        # Verify season belongs to user if provided
        season = serializer.validated_data.get('season')
        if season:
            get_object_or_404(Season, id=season.id, user=request.user)
        
        claim = serializer.save(user=request.user, status='draft')
        logger.info("Created insurance claim %d for user %s", claim.id, request.user.username)
        
        return Response({
            'message': 'Claim created successfully',
            'claim_id': claim.id,
            'status': claim.status,
        }, status=status.HTTP_201_CREATED)


class InsuranceClaimDetailView(APIView):
    """
    GET: Get claim details
    PATCH: Update claim
    DELETE: Delete draft claim
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get claim details"""
        claim = get_object_or_404(InsuranceClaim, id=pk, user=request.user)
        
        return Response({
            'id': claim.id,
            'field_id': claim.field_id,
            'field_name': claim.field.name if claim.field else None,
            'season_id': claim.season_id,
            'policy_number': claim.policy_number,
            'crop': claim.crop,
            'damage_type': claim.damage_type,
            'damage_type_display': claim.get_damage_type_display(),
            'damage_date': claim.damage_date.isoformat(),
            'damage_description': claim.damage_description,
            'area_affected_acres': float(claim.area_affected_acres),
            'estimated_loss': float(claim.estimated_loss),
            'claim_amount': float(claim.claim_amount) if claim.claim_amount else None,
            'status': claim.status,
            'status_display': claim.get_status_display(),
            'submitted_at': claim.submitted_at.isoformat() if claim.submitted_at else None,
            'reviewed_at': claim.reviewed_at.isoformat() if claim.reviewed_at else None,
            'reviewer_notes': claim.reviewer_notes,
            'bank_account': self._mask_account(claim.bank_account),
            'ifsc_code': claim.ifsc_code,
            'created_at': claim.created_at.isoformat(),
            'updated_at': claim.updated_at.isoformat(),
        })
    
    def patch(self, request, pk):
        """Update a claim (only draft claims can be fully edited)"""
        claim = get_object_or_404(InsuranceClaim, id=pk, user=request.user)
        data = request.data
        
        # Handle status change (submit claim)
        if 'status' in data:
            if data['status'] == 'submitted' and claim.status == 'draft':
                claim.status = 'submitted'
                claim.submitted_at = timezone.now()
                claim.save()
                return Response({
                    'message': 'Claim submitted successfully',
                    'claim_id': claim.id,
                    'status': claim.status,
                })
            elif claim.status != 'draft':
                return Response(
                    {'error': 'Only draft claims can be edited'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Only allow editing draft claims
        if claim.status != 'draft':
            return Response(
                {'error': 'Only draft claims can be edited'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InsuranceClaimSerializer(claim, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        return Response({
            'message': 'Claim updated successfully',
            'claim_id': claim.id,
        })
    
    def delete(self, request, pk):
        """Delete a draft claim"""
        claim = get_object_or_404(InsuranceClaim, id=pk, user=request.user)
        
        if claim.status != 'draft':
            return Response(
                {'error': 'Only draft claims can be deleted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        claim.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _mask_account(account_number: str) -> str:
        """Mask bank account number, showing only last 4 digits."""
        if not account_number or len(account_number) <= 4:
            return account_number
        return '●' * (len(account_number) - 4) + account_number[-4:]

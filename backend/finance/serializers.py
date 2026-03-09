"""
Serializers for finance module.
"""
from rest_framework import serializers
from django.db.models import Sum
from .models import Season, CostEntry, Revenue, CostCategory, InsuranceClaim


class SeasonSerializer(serializers.ModelSerializer):
    total_costs = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()
    
    class Meta:
        model = Season
        fields = [
            'id', 'name', 'season_type', 'year', 'start_date', 'end_date',
            'field', 'crop', 'is_active', 'total_costs', 'total_revenue', 'profit_loss'
        ]
        read_only_fields = ['id', 'total_costs', 'total_revenue', 'profit_loss']
    
    def get_total_costs(self, obj):
        # Use annotated value if available (prefetched), else single aggregate query
        if hasattr(obj, '_total_costs'):
            return obj._total_costs or 0
        return obj.costs.aggregate(total=Sum('amount'))['total'] or 0
    
    def get_total_revenue(self, obj):
        if hasattr(obj, '_total_revenue'):
            return obj._total_revenue or 0
        return obj.revenues.aggregate(total=Sum('total_amount'))['total'] or 0
    
    def get_profit_loss(self, obj):
        return self.get_total_revenue(obj) - self.get_total_costs(obj)


class CostEntrySerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = CostEntry
        fields = [
            'id', 'field', 'season', 'category', 'category_display',
            'description', 'amount', 'quantity', 'unit', 'date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_display']


class RevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revenue
        fields = [
            'id', 'field', 'season', 'crop', 'quantity_sold', 'unit',
            'price_per_unit', 'total_amount', 'buyer', 'date', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CostSummarySerializer(serializers.Serializer):
    """Summary of costs by category"""
    category = serializers.CharField()
    category_display = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    count = serializers.IntegerField()


class PnLSummarySerializer(serializers.Serializer):
    """Profit & Loss summary"""
    total_costs = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_loss = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    cost_breakdown = CostSummarySerializer(many=True)
    costs = CostEntrySerializer(many=True)
    revenues = RevenueSerializer(many=True)


class InsuranceClaimSerializer(serializers.ModelSerializer):
    """Full serializer for InsuranceClaim with validation."""
    damage_type_display = serializers.CharField(source='get_damage_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)
    masked_bank_account = serializers.SerializerMethodField()

    class Meta:
        model = InsuranceClaim
        fields = [
            'id', 'field', 'field_name', 'season', 'policy_number', 'crop',
            'area_affected_acres', 'damage_type', 'damage_type_display',
            'damage_date', 'damage_description', 'estimated_loss',
            'claim_amount', 'status', 'status_display',
            'submitted_at', 'reviewed_at', 'reviewer_notes',
            'masked_bank_account', 'ifsc_code',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'claim_amount', 'submitted_at', 'reviewed_at',
            'reviewer_notes', 'created_at', 'updated_at',
            'damage_type_display', 'status_display', 'field_name',
            'masked_bank_account',
        ]
        # bank_account is write-only (masked on read via get_masked_bank_account)
        extra_kwargs = {
            'bank_account': {'write_only': True, 'required': False},
        }

    def get_masked_bank_account(self, obj):
        acct = obj.bank_account or ''
        if len(acct) <= 4:
            return acct
        return '\u25cf' * (len(acct) - 4) + acct[-4:]

    def validate_area_affected_acres(self, value):
        if value <= 0:
            raise serializers.ValidationError("Area affected must be greater than zero.")
        return value

    def validate_estimated_loss(self, value):
        if value <= 0:
            raise serializers.ValidationError("Estimated loss must be greater than zero.")
        return value

    def validate_ifsc_code(self, value):
        import re
        if value and not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', value):
            raise serializers.ValidationError("Invalid IFSC code format.")
        return value

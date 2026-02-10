"""
Serializers for finance module.
"""
from rest_framework import serializers
from .models import Season, CostEntry, Revenue, CostCategory


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
        return sum(cost.amount for cost in obj.costs.all())
    
    def get_total_revenue(self, obj):
        return sum(rev.total_amount for rev in obj.revenues.all())
    
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

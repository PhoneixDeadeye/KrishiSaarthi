from django.contrib import admin
from .models import Season, CostEntry, Revenue, GovernmentScheme, InsuranceClaim


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'season_type', 'year', 'field', 'crop', 'is_active', 'start_date', 'end_date']
    list_filter = ['season_type', 'year', 'is_active']
    search_fields = ['name', 'crop']
    raw_id_fields = ['user', 'field']
    date_hierarchy = 'start_date'


@admin.register(CostEntry)
class CostEntryAdmin(admin.ModelAdmin):
    list_display = ['category', 'description', 'amount', 'field', 'season', 'date']
    list_filter = ['category', 'date']
    search_fields = ['description']
    raw_id_fields = ['user', 'field', 'season']
    date_hierarchy = 'date'


@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['crop', 'total_amount', 'quantity_sold', 'price_per_unit', 'field', 'date', 'buyer']
    list_filter = ['crop', 'date']
    search_fields = ['crop', 'buyer']
    raw_id_fields = ['user', 'field', 'season']
    date_hierarchy = 'date'


@admin.register(GovernmentScheme)
class GovernmentSchemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'scheme_type', 'is_active', 'min_land_acres', 'max_subsidy_amount', 'application_deadline']
    list_filter = ['scheme_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'crop', 'damage_type', 'status', 'estimated_loss', 'claim_amount', 'damage_date']
    list_filter = ['status', 'damage_type', 'damage_date']
    search_fields = ['crop', 'policy_number', 'user__username']
    raw_id_fields = ['user', 'field', 'season']
    date_hierarchy = 'damage_date'
    readonly_fields = ['created_at', 'updated_at']

from django.contrib import admin
from .models import Season, CostEntry, Revenue


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'season_type', 'year', 'field', 'crop', 'is_active']
    list_filter = ['season_type', 'year', 'is_active']
    search_fields = ['name', 'crop']


@admin.register(CostEntry)
class CostEntryAdmin(admin.ModelAdmin):
    list_display = ['category', 'description', 'amount', 'field', 'date']
    list_filter = ['category', 'date']
    search_fields = ['description']


@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['crop', 'total_amount', 'field', 'date', 'buyer']
    list_filter = ['crop', 'date']
    search_fields = ['crop', 'buyer']

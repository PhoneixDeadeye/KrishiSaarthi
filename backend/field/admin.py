"""Admin configuration for the field app."""
from django.contrib import admin
from .models import FieldData, Pest, FieldLog, FieldAlert, IrrigationLog


@admin.register(FieldData)
class FieldDataAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "cropType", "created_at")
    list_filter = ("cropType", "created_at")
    search_fields = ("name", "user__username", "cropType")
    readonly_fields = ("created_at",)
    raw_id_fields = ("user",)


@admin.register(Pest)
class PestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("user__username",)
    raw_id_fields = ("user",)


@admin.register(FieldLog)
class FieldLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "field", "date", "activity", "created_at")
    list_filter = ("activity", "date")
    search_fields = ("user__username", "details")
    raw_id_fields = ("user", "field")
    date_hierarchy = "date"


@admin.register(FieldAlert)
class FieldAlertAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "field", "date", "message", "is_read")
    list_filter = ("is_read", "date")
    search_fields = ("user__username", "message")
    raw_id_fields = ("user", "field", "log")


@admin.register(IrrigationLog)
class IrrigationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "field", "date", "source", "water_amount")
    list_filter = ("source", "date")
    search_fields = ("user__username", "field__name")
    raw_id_fields = ("user", "field")
    date_hierarchy = "date"
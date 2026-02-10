from rest_framework import serializers
from .models import FieldData, FieldLog, FieldAlert, Pest, IrrigationLog

class PestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pest
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class FieldDataResponseSerializer(serializers.Serializer):
    NDVI = serializers.FloatField(allow_null=True)
    EVI = serializers.FloatField(allow_null=True)
    SAVI = serializers.FloatField(allow_null=True)
    crop_type_class = serializers.FloatField(allow_null=True)
    rainfall_mm = serializers.FloatField(allow_null=True)
    temperature_K = serializers.FloatField(allow_null=True)
    soil_moisture = serializers.FloatField(allow_null=True)
    ndvi_time_series = serializers.ListField(
        child=serializers.DictField(), 
        allow_empty=True,
        required=False
    )
    ndwi_time_series = serializers.ListField(
        child=serializers.DictField(), 
        allow_empty=True,
        required=False
    )
    error = serializers.CharField(required=False, allow_null=True)
    details = serializers.CharField(required=False, allow_null=True)

class FieldDataSerializer(serializers.ModelSerializer):
    """Serializer for FieldData model"""
    class Meta:
        model = FieldData
        fields = ['id', 'user', 'name', 'cropType', 'polygon', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class FieldLogSerializer(serializers.ModelSerializer):
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldData.objects.all(), source='field', required=False, allow_null=True
    )

    class Meta:
        model = FieldLog
        fields = ['id', 'field_id', 'date', 'activity', 'details', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FieldAlertSerializer(serializers.ModelSerializer):
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldData.objects.all(), source='field', required=False, allow_null=True
    )

    class Meta:
        model = FieldAlert
        fields = ['id', 'field_id', 'log', 'date', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class IrrigationLogSerializer(serializers.ModelSerializer):
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldData.objects.all(), source='field', required=False, allow_null=True
    )
    field_name = serializers.CharField(source='field.name', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = IrrigationLog
        fields = ['id', 'field_id', 'field_name', 'date', 'water_amount', 
                  'duration_minutes', 'source', 'source_display', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

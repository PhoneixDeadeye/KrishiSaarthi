import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from config.pagination import get_optional_paginator

from ..models import FieldData
from ..serializers import FieldDataSerializer
from ..validators import validate_field_data, sanitize_coordinates

logger = logging.getLogger(__name__)


class FieldDataView(APIView):
    """
    GET: List all fields for the user
    DELETE: Delete a specific field by ID
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            fields = FieldData.objects.filter(user=request.user).order_by('-created_at')
            paginator = get_optional_paginator(request)
            if paginator is not None:
                page = paginator.paginate_queryset(fields, request)
                serializer = FieldDataSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = FieldDataSerializer(fields, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error("Error listing fields: %s", e)
            return Response({"error": "Failed to retrieve fields"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk=None):
        """Delete a field by ID"""
        if not pk:
            return Response(
                {"error": "Field ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            field = FieldData.objects.get(pk=pk, user=request.user)
            field.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FieldData.DoesNotExist:
            return Response(
                {"error": "Field not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class SavePolygon(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        """
        Create or update a field polygon with comprehensive validation.
        """
        try:
            polygon = request.data.get("polygon")
            crop_type = request.data.get("cropType", "")
            name = request.data.get("name", "My Field")
            field_id = request.data.get("id", None)

            # Validate request data
            is_valid, error_msg = validate_field_data(request.data)
            if not is_valid:
                return Response(
                    {"error": error_msg},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Sanitize coordinates (now raises ValueError on invalid data)
            try:
                polygon['coordinates'] = sanitize_coordinates(polygon['coordinates'])
            except ValueError as exc:
                return Response(
                    {"error": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if field_id:
                # Update existing field
                field_data = get_object_or_404(FieldData, id=field_id, user=request.user)
                field_data.polygon = polygon
                field_data.cropType = crop_type
                field_data.name = name
                field_data.save()
                created = False
                logger.info("Updated field %s for user %s", field_id, request.user.username)
            else:
                # Create new field
                field_data = FieldData.objects.create(
                    user=request.user,
                    polygon=polygon,
                    cropType=crop_type,
                    name=name
                )
                created = True
                logger.info("Created new field %s for user %s", field_data.id, request.user.username)

            return Response(
                {
                    "message": "Field saved successfully",
                    "created": created,
                    "id": field_data.id,
                    "name": field_data.name,
                    "polygon": field_data.polygon,
                    "cropType": field_data.cropType,
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error("Error saving polygon for user %s: %s", request.user.username, e)
            return Response(
                {"error": "Failed to save field"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Renamed from getCoord to follow PEP 8 naming conventions.
# The old name `getCoord` is preserved as an alias for backwards-compatibility.
class GetCoordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_id = request.query_params.get('field_id')
        if field_id:
            field_data = get_object_or_404(FieldData, id=field_id, user=request.user)
        else:
            field_data = FieldData.objects.filter(user=request.user).first()

        if not field_data:
            return Response({"coord": None})

        polygon = field_data.polygon
        coords = polygon.get("coordinates", [])
        first_coord = coords[0][0] if coords and coords[0] else None

        return Response({"coord": first_coord})


# Backwards-compatible alias
getCoord = GetCoordView


def get_polygon(user, field_id=None):
    """Get polygon data for a user's field."""
    try:
        if field_id:
            field_data = FieldData.objects.get(id=field_id, user=user)
        else:
            field_data = FieldData.objects.filter(user=user).first()
        return field_data.polygon if field_data else None
    except FieldData.DoesNotExist:
        return None

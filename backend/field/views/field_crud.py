import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

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
            fields = FieldData.objects.filter(user=request.user)
            serializer = FieldDataSerializer(fields, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error listing fields: {e}")
            return Response({"error": "Failed to retrieve fields"}, status=500)

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
            
            # Sanitize coordinates
            polygon['coordinates'] = sanitize_coordinates(polygon['coordinates'])

            if field_id:
                # Update existing field
                field_data = get_object_or_404(FieldData, id=field_id, user=request.user)
                field_data.polygon = polygon
                field_data.cropType = crop_type
                field_data.name = name
                field_data.save()
                created = False
                logger.info(f"Updated field {field_id} for user {request.user.username}")
            else:
                # Create new field
                field_data = FieldData.objects.create(
                    user=request.user,
                    polygon=polygon,
                    cropType=crop_type,
                    name=name
                )
                created = True
                logger.info(f"Created new field {field_data.id} for user {request.user.username}")

            return Response(
                {
                    "message": "Field saved successfully",
                    "created": created,
                    "id": field_data.id,
                    "name": field_data.name,
                    "polygon": field_data.polygon,
                    "cropType": field_data.cropType,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error saving polygon for user {request.user.username}: {e}")
            return Response(
                {"error": "Failed to save field"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class getCoord(APIView):
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

# get coordinates list
def get_polygon(user, field_id=None):
    try:
        if field_id:
            field_data = FieldData.objects.get(id=field_id, user=user)
        else:
            field_data = FieldData.objects.filter(user=user).first()
        return field_data.polygon if field_data else None
    except Exception:
        return None

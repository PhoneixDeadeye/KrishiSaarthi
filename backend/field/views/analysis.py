import logging
import traceback
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import FieldData, Pest
from ..serializers import FieldDataResponseSerializer, PestSerializer
from ..utils import fetchEEData, calculate_area_in_hectares

# Updated import to new package name
from ml_engine import (
    get_health_score, predict_risk_from_values, calculate_carbon_metrics,
    predict_health, detect_awd_from_ndwi
)

logger = logging.getLogger(__name__)

class EEAnalysisView(APIView):
    """
    GET: Perform EE analysis for a specific field or latest field
    """
    permission_classes=[IsAuthenticated]

    def get(self, request):
        try:
            # Check if field_id is provided
            field_id = request.query_params.get('field_id')
            field = None
            
            if field_id:
                field = get_object_or_404(FieldData, id=field_id, user=request.user)
            else:
                # Default to first field
                field = FieldData.objects.filter(user=request.user).first()
            
            if not field:
                return Response({"error": "No fields found"}, status=404)

            # Retrieve EE Data
            response_data = fetchEEData(user=request.user, field_id=field_id)
            
            if 'error' in response_data:
                return Response(response_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            resp_serializer = FieldDataResponseSerializer(data=response_data)
            resp_serializer.is_valid(raise_exception=True)

            return Response(resp_serializer.validated_data)

        except Exception as e:
            logger.error(traceback.format_exc())
            return Response({"error": "Failed to perform analysis"}, status=500)

class PestReport(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        List historical pest scans for the authenticated user.
        """
        try:
            pests = Pest.objects.filter(user=request.user).order_by('-uploaded_at')[:10]
            serializer = PestSerializer(pests, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching pest history: {e}")
            return Response(
                {"error": "Failed to fetch history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _validate_plant_image(self, image_path: str) -> dict:
        """
        Use Gemini Vision to verify the image contains a plant/crop.
        Returns: {"is_plant": bool, "message": str, "confidence": str}
        """
        import os
        import google.generativeai as genai
        from PIL import Image
        
        try:
            genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Load image
            img = Image.open(image_path)
            
            prompt = """Analyze this image and determine if it shows a plant, crop, leaf, or agricultural vegetation.
            
            Respond in this exact JSON format only:
            {"is_plant": true/false, "confidence": "high/medium/low", "detected": "description of what you see"}
            
            Rules:
            - is_plant = true ONLY if the image clearly shows plant/crop material (leaves, stems, fruits, vegetables, agricultural fields)
            - is_plant = false for: screenshots, UI elements, text, animals, buildings, random objects, human faces
            - Be strict - if unsure, say false"""
            
            response = model.generate_content([prompt, img])
            
            # Parse response
            import json
            import re
            text = response.text.strip()
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', text)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "is_plant": result.get("is_plant", False),
                    "confidence": result.get("confidence", "low"),
                    "detected": result.get("detected", "unknown")
                }
            
            return {"is_plant": False, "confidence": "low", "detected": "Could not analyze image"}
            
        except Exception as e:
            logger.warning(f"Plant validation failed: {e}. Proceeding with detection anyway.")
            # If validation fails, allow the image through (fail-open)
            return {"is_plant": True, "confidence": "unknown", "detected": "validation_error"}

    def post(self, request):
        """
        Upload and analyze pest/disease image using CNN model.
        First validates that the image contains a plant using Gemini Vision.
        """
        try:
            if 'image' not in request.FILES:
                return Response(
                    {"error": "No image file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = request.FILES['image']
            
            # Validate file size (max 10MB)
            if image_file.size > 10 * 1024 * 1024:
                return Response(
                    {"error": "Image file too large (max 10MB)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
            if image_file.content_type not in allowed_types:
                return Response(
                    {"error": "Invalid file type. Only JPEG and PNG allowed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded = Pest.objects.create(
                user=request.user,
                image=image_file
            )
            
            logger.info(f"Processing pest image for user {request.user.username}")
            
            # Validate that image contains a plant using Gemini Vision
            validation = self._validate_plant_image(uploaded.image.path)
            
            if not validation.get("is_plant", False):
                # Delete the uploaded image since it's not valid
                uploaded.delete()
                return Response({
                    "error": "Invalid image",
                    "message": f"This doesn't appear to be a plant or crop image. Detected: {validation.get('detected', 'non-plant content')}. Please upload a clear photo of your crop leaves or plants.",
                    "is_plant": False,
                    "detected": validation.get("detected", "unknown")
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Run CNN prediction
            result = predict_health(uploaded.image.path)
            
            # Add upload metadata
            result['upload_id'] = uploaded.id
            result['uploaded_at'] = uploaded.uploaded_at.isoformat()
            result['image_validated'] = True
            result['validation_confidence'] = validation.get("confidence", "unknown")
            
            return Response(result, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error processing pest report: {e}")
            return Response(
                {"error": "Failed to process image"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AWDreport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_id = request.query_params.get('field_id')
        data = fetchEEData(user=request.user, field_id=field_id)
        
        if 'error' in data:
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        ndwi_data = data.get("ndwi_time_series", [])

        # awd.py
        report = detect_awd_from_ndwi(ndwi_series=ndwi_data)
        return Response(report)
    
class CarbonCredit(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_id = request.query_params.get('field_id')
        
        if field_id:
            field = get_object_or_404(FieldData, id=field_id, user=request.user)
        else:
            field = FieldData.objects.filter(user=request.user).first()
            
        if not field:
            return Response({"error": "No field found"}, status=404)

        # 1. Calculate Area
        try:
            # Assuming polygon is GeoJSON-like: {'coordinates': [[[x,y]...]]}
            coords = field.polygon.get('coordinates', [])[0]
            area = calculate_area_in_hectares(coords)
        except Exception as e:
            return Response({"error": f"Area calculation failed"}, status=500)

        # 2. Get EE data for AWD detection
        ndwi_series = []
        ndwi_dates = []
        ee_warning = None
        try:
            ee_data = fetchEEData(user=request.user, field_instance=field)
            if 'error' not in ee_data:
                # Extract NDWI values and dates from time series: [{"date": "...", "NDWI": val}, ...] -> [val, ...], [date, ...]
                ndwi_time_series = ee_data.get("ndwi_time_series", [])
                for entry in ndwi_time_series:
                    if isinstance(entry, dict) and "NDWI" in entry:
                        ndwi_series.append(entry["NDWI"])
                        ndwi_dates.append(entry.get("date", ""))
            else:
                ee_warning = "Satellite data unavailable; carbon metrics are estimated."
        except Exception as e:
            logger.warning(f"EE fetch for carbon credit failed: {e}")
            ee_warning = "Satellite data unavailable; carbon metrics are estimated."

        # 3. Calculate Credits using robust model
        result = calculate_carbon_metrics(area_hectare=area, ndwi_series=ndwi_series, ndwi_dates=ndwi_dates)
        if ee_warning:
            result['warnings'] = [ee_warning]
        
        return Response(result)
    
class PestPrediction(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        field_id = request.query_params.get('field_id')
        # lstm.py
        data = fetchEEData(user=request.user, field_id=field_id)
        
        if 'error' in data:
             return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
             
        result = predict_risk_from_values(data)
        return Response(result)
    
class HealthScore(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Calculate comprehensive crop health score using multiple data sources.
        """
        try:
            field_id = request.query_params.get('field_id')
            
            # Fetch Earth Engine data
            data = fetchEEData(user=request.user, field_id=field_id)
            
            if 'error' in data:
                return Response(
                    {"error": "Failed to fetch satellite data", "details": data.get('details')},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            # Try to get latest pest image
            latest_pest = Pest.objects.filter(user=request.user).order_by('-uploaded_at').first()
            image_path = latest_pest.image.path if latest_pest else None

            # Extract latest NDVI value from time series
            ndvi_time_series = data.get('ndvi_time_series', [])
            ndvi_latest = 0.5  # Default fallback
            if ndvi_time_series and len(ndvi_time_series) > 0:
                # Get the most recent NDVI value from time series
                latest_entry = ndvi_time_series[-1]
                if isinstance(latest_entry, dict) and 'NDVI' in latest_entry:
                    ndvi_latest = latest_entry['NDVI']

            # Calculate health score
            result = get_health_score(
                image_path=image_path, 
                ndvi_latest=ndvi_latest,
                sequence=data
            )
            
            logger.info(f"Health score calculated for user {request.user.username}: {result['score']}")
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return Response(
                {"error": "Failed to calculate health score"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

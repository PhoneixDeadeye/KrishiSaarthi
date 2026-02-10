"""
Soil Advice API - AI-powered fertilizer and soil management recommendations.
Uses Gemini to provide personalized advice based on soil test values.
"""
import os
import logging
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))


class SoilAdviceView(APIView):
    """
    POST /field/soil-advice
    Body: { "N": 80, "P": 40, "K": 60, "pH": 6.5, "crop": "rice" (optional) }
    Returns AI-generated soil management recommendations.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        
        # Extract soil parameters
        try:
            nitrogen = float(data.get('N', 0))
            phosphorus = float(data.get('P', 0))
            potassium = float(data.get('K', 0))
            ph = float(data.get('pH', 7.0))
            crop = data.get('crop', 'general crops')
        except (ValueError, TypeError) as e:
            return Response(
                {'error': 'Invalid soil values. N, P, K, pH must be numbers.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build prompt for Gemini
        prompt = f"""You are an expert agricultural soil scientist. 
Based on the following soil test results, provide specific, actionable fertilizer and soil management recommendations.

Soil Test Results:
- Nitrogen (N): {nitrogen} kg/ha
- Phosphorus (P): {phosphorus} kg/ha  
- Potassium (K): {potassium} kg/ha
- Soil pH: {ph}
- Target Crop: {crop}

Provide your response in the following JSON format:
{{
    "overall_status": "Good/Moderate/Poor",
    "recommendations": [
        "First specific recommendation...",
        "Second specific recommendation...",
        "Third specific recommendation..."
    ],
    "fertilizer_suggestion": "Specific NPK ratio or fertilizer type to apply",
    "timing": "When to apply amendments",
    "caution": "Any warnings or things to avoid (or null if none)"
}}

Be practical and region-agnostic. Focus on actionable steps the farmer can take."""

        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={
                    "response_mime_type": "application/json"
                }
            )
            
            response = model.generate_content(prompt)
            
            # Parse the JSON response
            import json
            advice_data = json.loads(response.text)
            
            return Response({
                'success': True,
                'soil_values': {
                    'N': nitrogen,
                    'P': phosphorus,
                    'K': potassium,
                    'pH': ph
                },
                'crop': crop,
                'advice': advice_data
            })

        except json.JSONDecodeError as e:
            logger.warning(f"Gemini returned non-JSON response: {response.text}")
            # Fallback: return the raw text
            return Response({
                'success': True,
                'soil_values': {
                    'N': nitrogen,
                    'P': phosphorus,
                    'K': potassium,
                    'pH': ph
                },
                'crop': crop,
                'advice': {
                    'overall_status': 'Analysis Complete',
                    'recommendations': [response.text],
                    'fertilizer_suggestion': None,
                    'timing': None,
                    'caution': None
                }
            })
        except Exception as e:
            logger.error(f"Gemini Soil Advice Error: {e}", exc_info=True)
            return Response(
                {'error': f'AI service error: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY
            )

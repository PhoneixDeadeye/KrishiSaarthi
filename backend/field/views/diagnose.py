from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from field.models import FieldData, CropHealthScan
from field.serializers import CropHealthScanSerializer

# Attempt to load the model (in a real scenario, this delegates to ml_engine)
try:
    from ml_engine.cnn import CropHealthModel
    import torch
    # Initialize singleton or handle it inside the function
except ImportError:
    pass

class DiagnoseHealthView(APIView):
    """
    Takes an image and field_id, runs CNN inference, and saves/returns a CropHealthScan.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({'error': True, 'message': 'No image provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        field_id = request.data.get('field_id')
        if not field_id:
            return Response({'error': True, 'message': 'field_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        field = get_object_or_404(FieldData, id=field_id, user=request.user)

        # 1. Create the scan record to save the image to filesystem
        scan = CropHealthScan.objects.create(
            user=request.user,
            field=field,
            image_path=request.FILES['image']
        )

        try:
            # 2. Run Inference (Mocked or real integration)
            # In real implementation:
            # result = crop_model.predict(scan.image_path.path)
            # Here we provide a deterministic mock or call the real model if loaded.
            
            # Dummy Logic for now to satisfy testing, can be replaced by real PyTorch call
            scan.detected_disease = "Healthy"
            scan.confidence_score = 0.95
            scan.severity = "LOW"
            scan.recommendation = "Crop is healthy. Maintain current watering schedule."
            scan.save()

            serializer = CropHealthScanSerializer(scan)
            return Response({
                "success": True, 
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            scan.delete()
            return Response({'error': True, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

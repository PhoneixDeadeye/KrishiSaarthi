"""
Equipment views for managing farm equipment and bookings.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import Equipment, EquipmentBooking, EquipmentStatus
from ..serializers import EquipmentSerializer, EquipmentBookingSerializer


class EquipmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        """List equipment or get single equipment"""
        if pk:
            equipment = get_object_or_404(Equipment, pk=pk, user=request.user)
            serializer = EquipmentSerializer(equipment)
            return Response(serializer.data)
        
        equipment_list = Equipment.objects.filter(user=request.user).prefetch_related('bookings').order_by('name')
        
        # Filter by status
        eq_status = request.query_params.get('status')
        if eq_status:
            equipment_list = equipment_list.filter(status=eq_status)
        
        # Filter by type
        eq_type = request.query_params.get('type')
        if eq_type:
            equipment_list = equipment_list.filter(equipment_type__icontains=eq_type)
        
        serializer = EquipmentSerializer(equipment_list, many=True)
        
        return Response({
            'equipment': serializer.data,
            'summary': {
                'total': equipment_list.count(),
                'available': equipment_list.filter(status=EquipmentStatus.AVAILABLE).count(),
                'in_use': equipment_list.filter(status=EquipmentStatus.IN_USE).count(),
                'maintenance': equipment_list.filter(status=EquipmentStatus.MAINTENANCE).count(),
            }
        })
    
    def post(self, request):
        """Register new equipment"""
        serializer = EquipmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        """Update equipment details"""
        equipment = get_object_or_404(Equipment, pk=pk, user=request.user)
        serializer = EquipmentSerializer(equipment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        """Remove equipment from registry"""
        equipment = get_object_or_404(Equipment, pk=pk, user=request.user)
        equipment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EquipmentBookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, equipment_id=None):
        """List bookings for equipment"""
        if equipment_id:
            equipment = get_object_or_404(Equipment, pk=equipment_id, user=request.user)
            bookings = equipment.bookings.select_related('field').all()
        else:
            bookings = EquipmentBooking.objects.filter(equipment__user=request.user).select_related('equipment', 'field')
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        if start_date:
            bookings = bookings.filter(end_datetime__date__gte=start_date)
        
        end_date = request.query_params.get('end_date')
        if end_date:
            bookings = bookings.filter(start_datetime__date__lte=end_date)
        
        # Filter upcoming only
        upcoming = request.query_params.get('upcoming')
        if upcoming == 'true':
            bookings = bookings.filter(start_datetime__gte=timezone.now())
        
        serializer = EquipmentBookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    def post(self, request, equipment_id=None):
        """Create a new equipment booking"""
        if equipment_id:
            equipment = get_object_or_404(Equipment, pk=equipment_id, user=request.user)
            data = request.data.copy()
            data['equipment'] = equipment_id
        else:
            data = request.data
            equipment = get_object_or_404(Equipment, pk=data.get('equipment'), user=request.user)
        
        # Check for booking conflicts
        start = data.get('start_datetime')
        end = data.get('end_datetime')
        conflicts = EquipmentBooking.objects.filter(
            equipment=equipment,
            is_completed=False,
            start_datetime__lt=end,
            end_datetime__gt=start
        ).exists()
        
        if conflicts:
            return Response(
                {'error': 'Equipment already booked during this time'},
                status=status.HTTP_409_CONFLICT
            )
        
        serializer = EquipmentBookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Update equipment status
            equipment.status = EquipmentStatus.IN_USE
            equipment.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        """Update booking (e.g., mark as completed)"""
        booking = get_object_or_404(EquipmentBooking, pk=pk, equipment__user=request.user)
        serializer = EquipmentBookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # If marked complete, check if equipment can be set to available
            if booking.is_completed:
                has_active = booking.equipment.bookings.filter(
                    is_completed=False,
                    start_datetime__lte=timezone.now(),
                    end_datetime__gte=timezone.now()
                ).exists()
                if not has_active:
                    booking.equipment.status = EquipmentStatus.AVAILABLE
                    booking.equipment.save()
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        """Cancel a booking"""
        booking = get_object_or_404(EquipmentBooking, pk=pk, equipment__user=request.user)
        equipment = booking.equipment
        booking.delete()
        
        # Check if equipment should be set to available
        has_active = equipment.bookings.filter(
            is_completed=False,
            start_datetime__lte=timezone.now(),
            end_datetime__gte=timezone.now()
        ).exists()
        if not has_active:
            equipment.status = EquipmentStatus.AVAILABLE
            equipment.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

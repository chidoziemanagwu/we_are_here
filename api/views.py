from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.core.cache import cache
from .serializers import ServiceSerializer
from core.models import Service

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Get base queryset
        queryset = Service.objects.select_related('category')\
            .prefetch_related('demographic_tags')\
            .filter(is_active=True)

        # Apply filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        demographics = self.request.query_params.getlist('demographics')
        if demographics:
            queryset = queryset.filter(demographic_tags__slug__in=demographics)

        # Add distance if coordinates provided
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        if lat and lng:
            try:
                user_location = Point(float(lng), float(lat), srid=4326)
                queryset = queryset.annotate(
                    distance=Distance('location', user_location)
                ).order_by('distance')
            except (ValueError, TypeError):
                pass

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def update_status(self, request, pk=None):
        service = self.get_object()
        status = request.data.get('status')
        if status in dict(Service.CAPACITY_STATUS_CHOICES):
            service.capacity_status = status
            service.save()
            return Response({'status': 'success'})
        return Response({'status': 'error'}, status=400)
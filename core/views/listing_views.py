from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ..models import Service, Category, DemographicTag, ServiceCategory
from django.conf import settings
import requests
from math import radians, cos, sin, asin, sqrt
from django.core.cache import cache

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def get_coordinates_from_location(location):
    """Get latitude and longitude from a location string using Google Geocoding API"""
    cache_key = f"geocode_{location}"
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result

    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={settings.GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'OK':
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            result = {'lat': lat, 'lng': lng}
            cache.set(cache_key, result, 60*60*24)  # Cache for 24 hours
            return result
        return None
    except Exception as e:
        print(f"Error geocoding location: {e}")
        return None
    


class ServiceListingView(ListView):
    model = Service
    template_name = 'listings/service_listing.html'
    context_object_name = 'services'
    paginate_by = 10

    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True)

        # Filter by category if provided
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by demographic if provided
        demographic_slug = self.request.GET.get('demographic')
        if demographic_slug:
            queryset = queryset.filter(demographic_tags__slug=demographic_slug)

        # Filter by status if provided
        status = self.request.GET.get('status')
        if status and status.strip():  # Check if status is not empty
            queryset = queryset.filter(status=status)

        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(address__icontains=search_query)
            )

        # Location-based filtering
        location = self.request.GET.get('location')
        radius = self.request.GET.get('radius', '5')  # Default 5km

        if location:
            coordinates = get_coordinates_from_location(location)
            if coordinates:
                # Filter services with coordinates
                radius = float(radius)
                filtered_services = []

                for service in queryset:
                    if service.latitude and service.longitude:
                        distance = haversine(
                            coordinates['lng'], coordinates['lat'],
                            float(service.longitude), float(service.latitude)
                        )
                        if distance <= radius:
                            service.distance = round(distance, 1)
                            filtered_services.append(service)

                # Sort by distance
                return sorted(filtered_services, key=lambda x: x.distance)

        return queryset.distinct().order_by('-is_featured', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add all categories to context (this is what's missing)
        context['all_categories'] = ServiceCategory.objects.filter(is_active=True).order_by('priority', 'name')

        # Add categories with counts
        categories = ServiceCategory.objects.all()
        category_counts = []

        for category in categories:
            # Use the category object directly in the filter
            count = Service.objects.filter(
                category=category,
                is_active=True
            ).count()

            category_counts.append({
                'category': category,
                'count': count
            })

        context['category_counts'] = category_counts

        # Add demographics with counts
        demographics = DemographicTag.objects.all()
        demographic_counts = []

        for demographic in demographics:
            count = Service.objects.filter(
                demographic_tags=demographic,
                is_active=True
            ).count()

            demographic_counts.append({
                'demographic': demographic,
                'count': count
            })

        context['demographic_counts'] = demographic_counts

        # Add current filters to context
        context['current_category'] = None
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = ServiceCategory.objects.filter(slug=category_slug).first()

        context['current_demographic'] = self.request.GET.get('demographic', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['current_location'] = self.request.GET.get('location', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_radius'] = self.request.GET.get('radius', '5')

        return context
    


    
class CategoryListingView(ServiceListingView):
    def get_queryset(self):
        # Get base queryset from parent
        queryset = super().get_queryset()

        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add current category to context
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(ServiceCategory, slug=category_slug)

        return context
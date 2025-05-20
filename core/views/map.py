import requests
import json
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Q
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..models import Category, Service, DemographicTag, ServiceCategory
from django.conf import settings


class MapView(TemplateView):
    template_name = 'core/map.html'

    def get(self, request, *args, **kwargs):
        try:
            # Check if this is an AJAX request
            if request.GET.get('ajax') == 'true':
                # Get location parameters
                lat_param = self.request.GET.get('lat')
                lng_param = self.request.GET.get('lng')

                # Create cache key based on request parameters
                cache_key = f"services_data_{lat_param}_{lng_param}_{request.GET.get('category', '')}_{request.GET.get('status', '')}_{request.GET.get('demographic', '')}"

                # Try to get from cache first
                cached_data = cache.get(cache_key)
                if cached_data:
                    return JsonResponse(cached_data)

                # If not in cache, generate the data
                context = self.get_context_data(**kwargs)
                all_services = json.loads(context['all_services_json'])

                response_data = {
                    'services': all_services
                }

                # Cache for 15 minutes
                cache.set(cache_key, response_data, 60 * 15)

                return JsonResponse(response_data)

            # Regular request - proceed with template rendering
            return super().get(request, *args, **kwargs)
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in MapView: {str(e)}")

            # For AJAX requests, return error response
            if request.GET.get('ajax') == 'true':
                return JsonResponse({
                    'services': [],
                    'error': 'Service data could not be loaded'
                })

            # For regular page, continue with empty services
            context = self.get_context_data(**kwargs)
            context['services'] = []
            context['external_services'] = []
            context['error_message'] = 'Service data could not be loaded'
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all categories - cache these as they rarely change
        context['categories'] = self.get_cached_categories()
        context['demographics'] = self.get_cached_demographics()

        # Get filter parameters from URL
        category_param = self.request.GET.get('category', '')
        status_param = self.request.GET.get('status', '')
        demographic_param = self.request.GET.get('demographic', '')

        # Get location parameters
        lat_param = self.request.GET.get('lat')
        lng_param = self.request.GET.get('lng')

        # Parse filter parameters
        selected_categories = category_param.split(',') if category_param else []
        selected_statuses = status_param.split(',') if status_param else ['available', 'limited']
        selected_demographics = demographic_param.split(',') if demographic_param else []

        # Store selected filters in context
        context['selected_categories'] = selected_categories
        context['selected_statuses'] = selected_statuses
        context['selected_demographics'] = selected_demographics

        # Optimize query - use select_related for foreign keys
        services_query = Service.objects.select_related('category').all()

        # Apply filters efficiently
        filters = Q()
        if selected_categories:
            filters &= Q(category__slug__in=selected_categories)

        if selected_statuses:
            filters &= Q(status__in=selected_statuses)

        # For demographic filters - use prefetch_related for many-to-many
        if selected_demographics:
            services_query = services_query.prefetch_related('demographic_tags')
            filters &= Q(demographic_tags__slug__in=selected_demographics)

        # Apply all filters at once for better performance
        if filters:
            services_query = services_query.filter(filters).distinct()

        # Get services from database
        context['services'] = services_query

        # Get external services if lat/lng are provided
        context['external_services'] = []
        if lat_param and lng_param:
            try:
                lat = float(lat_param)
                lng = float(lng_param)

                # Cache external services by location
                cache_key = f"external_services_{lat:.4f}_{lng:.4f}"
                cached_services = cache.get(cache_key)

                if cached_services:
                    context['external_services'] = cached_services
                else:
                    context['external_services'] = self.get_nearby_services(lat, lng)
                    # Cache for 1 hour - external services don't change often
                    cache.set(cache_key, context['external_services'], 60 * 60)
            except (ValueError, TypeError):
                # Invalid coordinates, skip external services
                pass

        # Prepare combined JSON data for JavaScript
        all_services = []

        # Add database services - optimize by creating a list comprehension
        all_services = [{
            'id': service.id,
            'name': service.name,
            'slug': service.slug,
            'shortDescription': service.short_description,
            'category': service.category.name if service.category else 'Uncategorized',
            'status': service.status,
            'latitude': service.latitude,
            'longitude': service.longitude,
            'address': service.address or 'Address not available',
            'phone': service.phone or 'Phone not available',
            'website': service.website or '#',
            'openingHours': service.opening_hours or 'Hours not specified',
            'isExternal': False
        } for service in services_query]

        # Add external services
        all_services.extend(context['external_services'])

        # Add to context as JSON string
        context['all_services_json'] = json.dumps(all_services)

        return context

    def get_cached_categories(self):
        """Get categories with caching"""
        cache_key = "all_service_categories"
        categories = cache.get(cache_key)
        if not categories:
            categories = list(ServiceCategory.objects.all())
            cache.set(cache_key, categories, 60 * 60)  # Cache for 1 hour
        return categories

    def get_cached_demographics(self):
        """Get demographics with caching"""
        cache_key = "all_demographics"
        demographics = cache.get(cache_key)
        if not demographics:
            demographics = list(DemographicTag.objects.all())
            cache.set(cache_key, demographics, 60 * 60)  # Cache for 1 hour
        return demographics


    def get_nearby_services(self, lat, lng):
        """Fetch nearby services using Google Places API with detailed information"""
        # Check if user has exceeded rate limit
        session_key = f"api_calls_{self.request.session.session_key}"
        api_calls = cache.get(session_key, 0)

        if api_calls > 50:  # Limit to 50 calls per session
            return []

        # Increment counter
        cache.set(session_key, api_calls + 1, 60 * 60)  # Reset after 1 hour

        services = []

        # Define search types with prioritization
        # Primary services (most important) - will search in 1200m radius
        primary_types = {
            "homeless_shelter": "Shelters",
            "food": "Food Services",
            "hospital": "Medical Support",
            "pharmacy": "Medical Support"
        }

        # Secondary services - will search in 800m radius
        secondary_types = {
            "meal_delivery": "Food Services",
            "meal_takeaway": "Food Services",
            "doctor": "Medical Support",
            "health": "Medical Support",
            "mental_health": "Mental Health"
        }

        # Tertiary services - will search in 600m radius
        tertiary_types = {
            "clothing_store": "Clothing Support",
            "laundry": "Shower Facilities",
            "lawyer": "Legal Support",
            "employment_agency": "Employment Support"
        }

        try:
            api_key = settings.GOOGLE_MAPS_API_KEY

            # Process each priority group with appropriate radius
            for types_dict, radius in [
                (primary_types, 1200),  # ~15 min walk for essential services
                (secondary_types, 800),  # ~10 min walk
                (tertiary_types, 600)    # ~7 min walk
            ]:
                # Limit the number of results per type for better performance
                max_results = 5 if radius == 1200 else 3  # More results for primary services

                for place_type, category in types_dict.items():
                    # Create cache key for this specific search
                    cache_key = f"google_places_{lat:.4f}_{lng:.4f}_{place_type}_{radius}"
                    cached_results = cache.get(cache_key)

                    if cached_results:
                        services.extend(cached_results)
                        continue

                    # Places API URL
                    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    params = {
                        "location": f"{lat},{lng}",
                        "radius": radius,
                        "type": place_type,
                        "key": api_key
                    }

                    response = requests.get(url, params=params, timeout=3)
                    data = response.json()

                    type_services = []
                    # Only process limited number of results per type
                    for place in data.get('results', [])[:max_results]:
                        # Get place details for phone, website, and hours
                        # Only get full details for primary services
                        if place_type in primary_types:
                            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                            details_params = {
                                "place_id": place['place_id'],
                                "fields": "formatted_phone_number,website,opening_hours,url",
                                "key": api_key
                            }

                            details_response = requests.get(details_url, params=details_params, timeout=3)
                            details_data = details_response.json().get('result', {})

                            # Extract opening hours if available
                            opening_hours = "Hours not available"
                            if 'opening_hours' in details_data and 'weekday_text' in details_data['opening_hours']:
                                opening_hours = "\n".join(details_data['opening_hours']['weekday_text'])

                            service = {
                                'id': f"gp_{place['place_id']}",
                                'name': place['name'],
                                'shortDescription': f"{category} service",
                                'category': category,
                                'status': 'available',
                                'latitude': place['geometry']['location']['lat'],
                                'longitude': place['geometry']['location']['lng'],
                                'address': place.get('vicinity', 'Address not available'),
                                'phone': details_data.get('formatted_phone_number', 'Phone not available'),
                                'website': details_data.get('website', details_data.get('url', '#')),
                                'openingHours': opening_hours,
                                'isExternal': True
                            }
                        else:
                            # For secondary and tertiary services, skip detailed API call for speed
                            service = {
                                'id': f"gp_{place['place_id']}",
                                'name': place['name'],
                                'shortDescription': f"{category} service",
                                'category': category,
                                'status': 'available',
                                'latitude': place['geometry']['location']['lat'],
                                'longitude': place['geometry']['location']['lng'],
                                'address': place.get('vicinity', 'Address not available'),
                                'phone': 'Phone not available',
                                'website': f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}",
                                'openingHours': 'Hours not available',
                                'isExternal': True
                            }

                        type_services.append(service)

                    # Cache these results for 24 hours
                    cache.set(cache_key, type_services, 60 * 60 * 24)
                    services.extend(type_services)

        except Exception as e:
            print(f"Error fetching from Google Places API: {e}")

        return services

    def _get_address_from_tags(self, tags):
        """Helper method to extract address from OSM tags"""
        if 'addr:full' in tags:
            return tags['addr:full']

        address_parts = []
        if 'addr:housenumber' in tags:
            address_parts.append(tags['addr:housenumber'])
        if 'addr:street' in tags:
            address_parts.append(tags['addr:street'])
        if 'addr:city' in tags:
            address_parts.append(tags['addr:city'])
        if 'addr:postcode' in tags:
            address_parts.append(tags['addr:postcode'])

        address = ' '.join(address_parts)
        return address if address else 'Address not available'
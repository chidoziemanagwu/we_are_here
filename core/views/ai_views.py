from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
import json
from ..helpers.ai_helper import AIAssistant
from ..models import Service

class AIAssistantView(TemplateView):
    template_name = "ai_assistant.html"

@csrf_protect
def ai_chat_endpoint(request):
    if request.method == 'POST':
        try:
            # Parse request
            data = json.loads(request.body)
            user_message = data.get('message', '')

            # Extract location from message if provided
            location_from_message = data.get('location', None)

            # Check if this is a list request
            is_list_request = any(term in user_message.lower() for term in
                                ["list", "show me", "give me a list", "show a list", "show as a list"])

            # Create a new assistant instance
            assistant = AIAssistant()

            # Get user location if available
            user_location = None

            # First check if location was explicitly provided in the request
            if location_from_message:
                user_location = location_from_message
            # Otherwise check if we have coordinates from the user profile
            elif request.user.is_authenticated:
                profile = getattr(request.user, 'profile', None)
                if profile and hasattr(profile, 'latitude') and hasattr(profile, 'longitude'):
                    if profile.latitude and profile.longitude:
                        user_location = (profile.latitude, profile.longitude)

            # Try to extract location from the message if not already found
            if not user_location:
                # Simple location extraction - look for "in [location]" or "near [location]" patterns
                location_patterns = [
                    r'(?:in|at|near|around)\s+([A-Z][A-Za-z\s\-]+(?:,\s*[A-Z][A-Za-z\s\-]+)*)',
                    r'(?:find|looking for|need).*(?:in|at|near|around)\s+([A-Z][A-Za-z\s\-]+(?:,\s*[A-Z][A-Za-z\s\-]+)*)'
                ]

                for pattern in location_patterns:
                    import re
                    match = re.search(pattern, user_message)
                    if match:
                        user_location = match.group(1).strip()
                        break

            # Get AI response with web search capabilities
            response_data = assistant.get_response(user_message, user_location)

            # Add list request flag
            response_data['is_list_request'] = is_list_request

            # Add the location we used to the response
            response_data['location_used'] = user_location

            # If the AI didn't find any services but suggested service types, look them up
            if "suggested_service_types" in response_data and not response_data.get("nearby_services"):
                nearby_services = []

                for service_type in response_data.get("suggested_service_types", []):
                    services = Service.objects.filter(
                        category__name__icontains=service_type,
                        is_active=True
                    ).order_by('name')[:3]

                    for service in services:
                        distance = None
                        if isinstance(user_location, tuple) and len(user_location) == 2 and hasattr(service, 'distance_from'):
                            try:
                                distance = service.distance_from(user_location)
                            except:
                                pass

                        nearby_services.append({
                            'id': service.id,
                            'name': service.name,
                            'category': service.category.name,
                            'address': service.address,
                            'phone': service.phone if hasattr(service, 'phone') else None,
                            'website': service.website if hasattr(service, 'website') else None,
                            'hours': service.hours if hasattr(service, 'hours') else None,
                            'distance': distance
                        })

                # Format services as HTML list if this is a list request
                                # Format services as HTML list if this is a list request
                if nearby_services and is_list_request:
                    # Create a clean introduction without bullet points
                    location_text = f" near {user_location}" if user_location else ""
                    intro = f"<p>I see that you're looking for services{location_text}. Here are some options that might be helpful:</p>\n"

                    # Format list with proper bullet points for each service
                    formatted_list = "<ul class='list-disc pl-5 space-y-2 mt-2'>\n"
                    for service in nearby_services:
                        formatted_list += f"<li><strong>{service['name']}</strong>\n"

                        # Create a nested list for details
                        formatted_list += "<ul class='list-disc pl-5 mt-1'>\n"
                        if service.get('address'):
                            formatted_list += f"<li>Address: {service['address']}</li>\n"
                        if service.get('phone'):
                            formatted_list += f"<li>Phone: {service['phone']}</li>\n"
                        if service.get('website'):
                            formatted_list += f"<li>Website: <a href='{service['website']}' class='text-blue-600 hover:underline' target='_blank'>{service['name']}</a></li>\n"
                        if service.get('hours'):
                            formatted_list += f"<li>Hours: {service['hours']}</li>\n"
                        if service.get('services'):
                            formatted_list += f"<li>Services: {service['services']}</li>\n"
                        formatted_list += "</ul>\n"

                        formatted_list += "</li>\n"
                    formatted_list += "</ul>"

                    # Add a clean outro
                    outro = "<p>These shelters offer temporary accommodation and support services for individuals in need. Feel free to reach out to them for assistance.</p>"

                    # Combine all parts
                    response_data["response"] = intro + formatted_list + outro

                if nearby_services:
                    response_data["nearby_services"] = nearby_services

            return JsonResponse(response_data)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({
                "response": f"I'm sorry, I encountered a problem: {str(e)}",
                "error": str(e)
            }, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
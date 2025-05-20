from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.filter(is_safe=True)
def json_script(value):
    """Convert a Python value to JSON string"""
    return mark_safe(json.dumps(value))

@register.filter
def status_badge_class(status):
    """Return appropriate CSS classes for status badges"""
    classes = {
        'AVAILABLE': 'bg-green-100 text-green-800',
        'LIMITED': 'bg-yellow-100 text-yellow-800',
        'FULL': 'bg-red-100 text-red-800',
        'CLOSED': 'bg-gray-100 text-gray-800'
    }
    return classes.get(status, 'bg-gray-100 text-gray-800')

@register.inclusion_tag('components/form_field.html')
def render_field(field):
    """Render a form field with proper styling and error handling"""
    return {'field': field}

@register.simple_tag
def active_link(request, pattern):
    """Return 'active' if the pattern matches the current URL"""
    import re
    if re.search(pattern, request.path):
        return 'bg-gray-100'
    return ''

@register.filter
def phone_format(phone_number):
    """Format phone number for display"""
    if not phone_number:
        return ''
    # Remove any non-digit characters
    clean_number = ''.join(filter(str.isdigit, str(phone_number)))
    if len(clean_number) == 10:
        return f"({clean_number[:3]}) {clean_number[3:6]}-{clean_number[6:]}"
    elif len(clean_number) == 11:
        return f"+{clean_number[0]} ({clean_number[1:4]}) {clean_number[4:7]}-{clean_number[7:]}"
    return phone_number

@register.filter
def time_slot_format(time_slot):
    """Format time slot for display"""
    if isinstance(time_slot, dict):
        start = time_slot.get('start', '')
        end = time_slot.get('end', '')
        if start and end:
            return f"{start} - {end}"
    return 'Closed'
from django import template
from django.utils.http import urlencode

register = template.Library()

@register.simple_tag
def build_url_params(search_query=None, location=None, status=None, demographic=None):
    """Build URL parameters for filtering"""
    params = {}
    if search_query:
        params['q'] = search_query
    if location:
        params['location'] = location
    if status:
        params['status'] = status
    if demographic:
        params['demographic'] = demographic

    if params:
        return '?' + urlencode(params)
    return ''
# core/views/__init__.py

# Import function-based views from their respective modules
from .map import MapView
from .service import ServiceDetailView, service_status_update

# Export these names
__all__ = ['MapView', 'ServiceDetailView', 'service_status_update']
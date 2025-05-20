# core/views.py
from django.views.generic import TemplateView, DetailView
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Service, ServiceCategory, DemographicTag

class MapView(TemplateView):
    template_name = 'core/map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.filter(is_active=True)
        context['demographics'] = DemographicTag.objects.filter(is_active=True)

        # Get services
        services = Service.objects.select_related('category')\
            .prefetch_related('demographic_tags')\
            .filter(is_active=True)

        # Filter by category if provided
        category = self.request.GET.get('category')
        if category:
            services = services.filter(category__slug=category)

        # Filter by status if provided
        status = self.request.GET.getlist('status')
        if status:
            services = services.filter(status__in=status)

        # Order services
        services = services.order_by('category__priority', 'name')

        context['services'] = services
        return context

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'core/service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def service_status_update(request, pk):
    """AJAX endpoint for updating service status"""
    if not request.method == 'POST':
        return HttpResponseBadRequest(
            JsonResponse({'status': 'error', 'message': 'Method not allowed'})
        )

    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponseBadRequest(
            JsonResponse({'status': 'error', 'message': 'AJAX requests only'})
        )

    try:
        service = Service.objects.get(pk=pk)
        status = request.POST.get('status')

        # Check if status is valid
        valid_statuses = [choice[0] for choice in Service.STATUS_CHOICES]
        if status in valid_statuses:
            service.status = status
            service.save(update_fields=['status'])
            return JsonResponse({
                'status': 'success',
                'data': {
                    'status': status,
                    'status_display': dict(Service.STATUS_CHOICES)[status]
                }
            })
        else:
            return HttpResponseBadRequest(
                JsonResponse({
                    'status': 'error',
                    'message': 'Invalid status value'
                })
            )

    except Service.DoesNotExist:
        return HttpResponseBadRequest(
            JsonResponse({
                'status': 'error',
                'message': 'Service not found'
            })
        )
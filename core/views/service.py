# core/views/service.py
from django.views.generic import DetailView
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from ..models import Service

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
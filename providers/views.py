from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import ServiceProvider, ServiceUpdate
from core.models import Service

class ProviderDashboardView(LoginRequiredMixin, ListView):
    template_name = 'providers/dashboard.html'
    context_object_name = 'services'

    def get_queryset(self):
        provider = get_object_or_404(ServiceProvider, user=self.request.user)
        return provider.services.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provider = get_object_or_404(ServiceProvider, user=self.request.user)
        context['provider'] = provider
        context['recent_updates'] = ServiceUpdate.objects.filter(
            provider=provider
        ).select_related('service')[:5]
        return context

class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Service
    template_name = 'providers/service_update.html'
    fields = ['capacity_status']
    success_url = reverse_lazy('provider_dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        provider = get_object_or_404(ServiceProvider, user=self.request.user)
        ServiceUpdate.objects.create(
            service=self.object,
            provider=provider,
            status=self.object.capacity_status
        )
        return response
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Count
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from ..models import Service, ServiceCategory, Category, DemographicTag
from ..forms import ServiceForm, CategoryForm

User = get_user_model()

# Base Admin Mixin to check if user is staff or superuser
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'admin_login'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "You don't have permission to access the admin portal.")
            return redirect('home')
        return super().handle_no_permission()

# Admin Login
class AdminLoginView(LoginView):
    template_name = 'admin/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse_lazy('admin_dashboard')
        return reverse_lazy('home')

    def form_valid(self, form):
        # Check if user is staff or superuser
        user = form.get_user()
        if not (user.is_staff or user.is_superuser):
            form.add_error(None, "You don't have permission to access the admin portal.")
            return self.form_invalid(form)
        return super().form_valid(form)

# Admin Dashboard
class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/dashboard.html'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Use ServiceCategory instead of Category
        context['services_by_category'] = ServiceCategory.objects.annotate(
            service_count=Count('services')
        ).order_by('-service_count')

        context['total_services'] = Service.objects.count()
        context['active_services'] = Service.objects.filter(is_active=True).count()
        context['total_categories'] = ServiceCategory.objects.count()
        context['total_demographics'] = DemographicTag.objects.count()

        # Recent services
        context['recent_services'] = Service.objects.order_by('-created_at')[:5]

        return context


# Service Management
class AdminServiceListView(AdminRequiredMixin, ListView):
    model = Service
    template_name = 'admin/service_list.html'
    context_object_name = 'services'
    paginate_by = 20

    def get_queryset(self):
        queryset = Service.objects.all().order_by('-updated_at')

        # Filter by category if provided
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by active status if provided
        is_active = self.request.GET.get('is_active')
        if is_active:
            is_active = is_active == 'true'
            queryset = queryset.filter(is_active=is_active)

        # Search by name or address
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                name__icontains=search
            ) | queryset.filter(
                address__icontains=search
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        # Add current filters to context
        context['current_category'] = self.request.GET.get('category', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_is_active'] = self.request.GET.get('is_active', '')
        context['current_search'] = self.request.GET.get('search', '')

        return context

class AdminServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'admin/service_form.html'
    success_url = reverse_lazy('admin_service_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Service'
        context['submit_text'] = 'Create Service'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Service created successfully!')
        return super().form_valid(form)

class AdminServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'admin/service_form.html'
    success_url = reverse_lazy('admin_service_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Service: {self.object.name}'
        context['submit_text'] = 'Update Service'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Service updated successfully!')
        return super().form_valid(form)

class AdminServiceDeleteView(AdminRequiredMixin, DeleteView):
    model = Service
    template_name = 'admin/service_confirm_delete.html'
    success_url = reverse_lazy('admin_service_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Service deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Category Management
class AdminCategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'admin/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # The Category model doesn't have a 'services' related field
        # We need to use a different approach to count services

        # Option 1: If Service has a direct ForeignKey to Category
        # return Category.objects.annotate(service_count=Count('service_set')).order_by('name')

        # Option 2: Since you're using ServiceCategory for services, not Category
        # We can't directly count services from Category
        # Just return categories without the count for now
        return Category.objects.all().order_by('name')

class AdminCategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'admin/category_form.html'
    success_url = reverse_lazy('admin_category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Category'
        context['submit_text'] = 'Create Category'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

class AdminCategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'admin/category_form.html'
    success_url = reverse_lazy('admin_category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Category: {self.object.name}'
        context['submit_text'] = 'Update Category'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)

class AdminCategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'admin/category_confirm_delete.html'
    success_url = reverse_lazy('admin_category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)

# User Management
class AdminUserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')

        # Filter by staff status if provided
        is_staff = self.request.GET.get('is_staff')
        if is_staff:
            is_staff = is_staff == 'true'
            queryset = queryset.filter(is_staff=is_staff)

        # Filter by active status if provided
        is_active = self.request.GET.get('is_active')
        if is_active:
            is_active = is_active == 'true'
            queryset = queryset.filter(is_active=is_active)

        # Search by username or email
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add current filters to context
        context['current_is_staff'] = self.request.GET.get('is_staff', '')
        context['current_is_active'] = self.request.GET.get('is_active', '')
        context['current_search'] = self.request.GET.get('search', '')

        return context

# Subscriber Management
class AdminSubscriberListView(AdminRequiredMixin, ListView):
    template_name = 'admin/subscriber_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 20

    def get_queryset(self):
        try:
            from ..models import ServiceSubscription
            queryset = ServiceSubscription.objects.all().order_by('-created_at')

            # Filter by service if provided
            service_id = self.request.GET.get('service')
            if service_id:
                queryset = queryset.filter(service_id=service_id)

            # Filter by status if provided
            status = self.request.GET.get('status')
            if status:
                queryset = queryset.filter(status=status)

            # Search by user email or name
            search = self.request.GET.get('search')
            if search:
                queryset = queryset.filter(
                    user__email__icontains=search
                ) | queryset.filter(
                    user__username__icontains=search
                )

            return queryset
        except:
            # Model doesn't exist yet
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()

        # Add current filters to context
        context['current_service'] = self.request.GET.get('service', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')

        return context

# Message Request Management
class AdminMessageRequestListView(AdminRequiredMixin, ListView):
    template_name = 'admin/message_request_list.html'
    context_object_name = 'message_requests'
    paginate_by = 20

    def get_queryset(self):
        try:
            from ..models import MessageRequest
            queryset = MessageRequest.objects.all().order_by('-created_at')

            # Filter by service if provided
            service_id = self.request.GET.get('service')
            if service_id:
                queryset = queryset.filter(service_id=service_id)

            # Filter by status if provided
            status = self.request.GET.get('status')
            if status:
                queryset = queryset.filter(status=status)

            # Search by user email or name
            search = self.request.GET.get('search')
            if search:
                queryset = queryset.filter(
                    user__email__icontains=search
                ) | queryset.filter(
                    user__username__icontains=search
                ) | queryset.filter(
                    message__icontains=search
                )

            return queryset
        except:
            # Model doesn't exist yet
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()

        # Add current filters to context
        context['current_service'] = self.request.GET.get('service', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')

        return context

# Check-in Request Management
class AdminCheckinListView(AdminRequiredMixin, ListView):
    template_name = 'admin/checkin_list.html'
    context_object_name = 'checkin_requests'
    paginate_by = 20

    def get_queryset(self):
        try:
            from ..models import CheckinRequest
            queryset = CheckinRequest.objects.all().order_by('-created_at')

            # Filter by service if provided
            service_id = self.request.GET.get('service')
            if service_id:
                queryset = queryset.filter(service_id=service_id)

            # Filter by status if provided
            status = self.request.GET.get('status')
            if status:
                queryset = queryset.filter(status=status)

            # Search by user email or name
            search = self.request.GET.get('search')
            if search:
                queryset = queryset.filter(
                    user__email__icontains=search
                ) | queryset.filter(
                    user__username__icontains=search
                )

            return queryset
        except:
            # Model doesn't exist yet
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()

        # Add current filters to context
        context['current_service'] = self.request.GET.get('service', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')

        return context
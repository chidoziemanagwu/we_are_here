from django.urls import path
from .views import MapView, ServiceDetailView, service_status_update
from .views.ai_views import AIAssistantView, ai_chat_endpoint
from .views.auth_views import RegisterView
from .views.listing_views import ServiceListingView, CategoryListingView
from .views.admin_views import (
    AdminLoginView, AdminDashboardView, AdminServiceListView,
    AdminServiceCreateView, AdminServiceUpdateView, AdminServiceDeleteView,
    AdminSubscriberListView, AdminMessageRequestListView, AdminCheckinListView,
    AdminUserListView, AdminCategoryListView, AdminCategoryCreateView,
    AdminCategoryUpdateView, AdminCategoryDeleteView
)

urlpatterns = [
    path('', MapView.as_view(), name='home'),
    path('service/<slug:slug>/', ServiceDetailView.as_view(), name='service_detail'),
    path('service/<int:pk>/status/', service_status_update, name='service_status_update'),

    # AI Assistant URLs
    path('ai-assistant/', AIAssistantView.as_view(), name='ai_assistant'),
    path('ai-chat/', ai_chat_endpoint, name='ai_chat_endpoint'),


    # Listing URLs
    path('listings/', ServiceListingView.as_view(), name='service_listing'),
    path('listings/category/<slug:category_slug>/', CategoryListingView.as_view(), name='category_listing'),

    path('accounts/register/', RegisterView.as_view(), name='register'),


    # Admin URLs
    path('admin-portal/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin-portal/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),

    # Admin Service Management
    path('admin-portal/services/', AdminServiceListView.as_view(), name='admin_service_list'),
    path('admin-portal/services/create/', AdminServiceCreateView.as_view(), name='admin_service_create'),
    path('admin-portal/services/<slug:slug>/edit/', AdminServiceUpdateView.as_view(), name='admin_service_update'),
    path('admin-portal/services/<slug:slug>/delete/', AdminServiceDeleteView.as_view(), name='admin_service_delete'),

    # Admin Category Management
    path('admin-portal/categories/', AdminCategoryListView.as_view(), name='admin_category_list'),
    path('admin-portal/categories/create/', AdminCategoryCreateView.as_view(), name='admin_category_create'),
    path('admin-portal/categories/<slug:slug>/edit/', AdminCategoryUpdateView.as_view(), name='admin_category_update'),
    path('admin-portal/categories/<slug:slug>/delete/', AdminCategoryDeleteView.as_view(), name='admin_category_delete'),

    # Admin User Management
    path('admin-portal/users/', AdminUserListView.as_view(), name='admin_user_list'),

    # Admin Subscriber/Request Management
    path('admin-portal/subscribers/', AdminSubscriberListView.as_view(), name='admin_subscriber_list'),
    path('admin-portal/message-requests/', AdminMessageRequestListView.as_view(), name='admin_message_request_list'),
    path('admin-portal/checkins/', AdminCheckinListView.as_view(), name='admin_checkin_list'),
]
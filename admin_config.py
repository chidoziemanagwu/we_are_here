# admin_config.py
from custom_admin import django_admin_site
from django.contrib import admin
from core.models import (
    ServiceCategory,
    DemographicTag,
    Service,
    ServiceProvider,
    Category,
    ServiceSubscription,
    MessageRequest,
    CheckinRequest
)

# Custom ModelAdmin classes
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class DemographicTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'is_active', 'is_verified', 'is_featured')
    list_filter = ('category', 'status', 'is_active', 'is_verified', 'is_featured', 'demographic_tags')
    search_fields = ('name', 'description', 'address')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('demographic_tags',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'demographic_tags')
        }),
        ('Service Details', {
            'fields': ('short_description', 'description', 'opening_hours')
        }),
        ('Location', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'is_verified', 'is_featured')
        }),
        ('Verification', {
            'fields': ('last_verified_date', 'verified_by', 'notes')
        }),
    )

class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'contact_person', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('organization_name', 'contact_person', 'user__username')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class ServiceSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'service__name', 'notes')

class MessageRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'service__name', 'message')

class CheckinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'status', 'scheduled_for', 'created_at')
    list_filter = ('status', 'created_at', 'scheduled_for')
    search_fields = ('user__username', 'service__name', 'notes')

# Register models with the custom admin site
django_admin_site.register(ServiceCategory, ServiceCategoryAdmin)
django_admin_site.register(DemographicTag, DemographicTagAdmin)
django_admin_site.register(Service, ServiceAdmin)
django_admin_site.register(ServiceProvider, ServiceProviderAdmin)
django_admin_site.register(Category, CategoryAdmin)
django_admin_site.register(ServiceSubscription, ServiceSubscriptionAdmin)
django_admin_site.register(MessageRequest, MessageRequestAdmin)
django_admin_site.register(CheckinRequest, CheckinRequestAdmin)
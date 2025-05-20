from django.contrib import admin
from .models import Service, ServiceCategory, DemographicTag

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'status', 'is_active']
    list_filter = ['category', 'status', 'is_active']
    search_fields = ['name', 'description', 'address']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DemographicTag)
class DemographicTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
from django import forms
from .models import Service, Category, ServiceCategory, DemographicTag, ServiceProvider, ServiceSubscription, MessageRequest, CheckinRequest

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'name', 'category', 'short_description', 'description',
            'address', 'latitude', 'longitude', 'phone', 'email', 'website',
            'status', 'is_active', 'is_verified', 'is_featured',
            'opening_hours', 'demographic_tags', 'notes'
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'opening_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'demographic_tags': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'icon', 'is_active', 'priority']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-home'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'slug', 'description', 'icon', 'priority', 'is_active', 'is_featured', 'color_code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-home'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control'}),
            'color_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '#FF5733'}),
        }

class DemographicTagForm(forms.ModelForm):
    class Meta:
        model = DemographicTag
        fields = ['name', 'slug', 'description', 'icon', 'is_active', 'badge_color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-users'}),
            'badge_color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '#4F46E5'}),
        }

class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = [
            'organization_name', 'contact_person', 'phone', 'address',
            'website', 'is_verified', 'notes'
        ]
        widgets = {
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ServiceSubscriptionForm(forms.ModelForm):
    class Meta:
        model = ServiceSubscription
        fields = ['service', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MessageRequestForm(forms.ModelForm):
    class Meta:
        model = MessageRequest
        fields = ['service', 'message', 'status', 'admin_notes']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CheckinRequestForm(forms.ModelForm):
    class Meta:
        model = CheckinRequest
        fields = ['service', 'notes', 'scheduled_for', 'status', 'admin_notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scheduled_for': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
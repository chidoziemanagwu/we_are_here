from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django import forms
from django.contrib.auth.models import User

class ServiceProviderRegistrationForm(UserCreationForm):
    organization_name = forms.CharField(max_length=255)
    contact_person = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    verification_document = forms.FileField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = ServiceProviderRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()

        # Create service provider profile
        from ..models import ServiceProvider
        ServiceProvider.objects.create(
            user=user,
            organization_name=form.cleaned_data['organization_name'],
            contact_person=form.cleaned_data['contact_person'],
            phone=form.cleaned_data['phone'],
            verification_document=form.cleaned_data['verification_document']
        )

        login(self.request, user)
        return redirect(self.success_url)
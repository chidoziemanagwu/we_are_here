from django.db import models
from django.contrib.auth.models import User
from core.models import Service

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, related_name='providers')
    organization_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=17)
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verification_docs/', blank=True)

    def __str__(self):
        return self.organization_name

class ServiceUpdate(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Service.CAPACITY_STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
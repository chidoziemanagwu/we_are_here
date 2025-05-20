from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., fa-home)")
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # New fields for admin
    is_featured = models.BooleanField(default=False)
    color_code = models.CharField(max_length=20, blank=True, help_text="Color code for map markers (e.g., #FF5733)")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_listing', kwargs={'category_slug': self.slug})

    class Meta:
        verbose_name_plural = 'Service Categories'
        ordering = ['priority', 'name']


class DemographicTag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # New fields for admin
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., fa-users)")
    badge_color = models.CharField(max_length=20, default="#4F46E5", help_text="Color for demographic badge")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Service(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.TextField(max_length=500)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    # Status choices
    STATUS_AVAILABLE = 'available'
    STATUS_LIMITED = 'limited'
    STATUS_UNAVAILABLE = 'unavailable'

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_LIMITED, 'Limited Availability'),
        (STATUS_UNAVAILABLE, 'Unavailable'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE
    )

    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name='services')
    demographic_tags = models.ManyToManyField(DemographicTag, blank=True, related_name='services')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New fields for admin
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    opening_hours = models.CharField(max_length=255, blank=True)
    last_verified_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_services')
    notes = models.TextField(blank=True, help_text="Admin notes about this service")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def distance_from(self, coordinates):
        """Calculate distance from coordinates (lat, lng) to this service"""
        from math import radians, cos, sin, asin, sqrt

        # Haversine formula for calculating distance between two points on Earth
        def haversine(lat1, lon1, lat2, lon2):
            # Convert decimal degrees to radians
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

            # Haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 3956  # Radius of Earth in miles
            return c * r

        user_lat, user_lng = coordinates
        return haversine(user_lat, user_lng, self.latitude, self.longitude)

    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-is_featured', 'name']


class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider')
    organization_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    verification_document = models.FileField(upload_to='verification_documents/')
    is_verified = models.BooleanField(default=False)

    # New fields for admin
    verified_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_providers')
    notes = models.TextField(blank=True, help_text="Admin notes about this provider")
    address = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization_name


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    # New fields for admin
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., fa-home)")
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['priority', 'name']


# New models for subscriptions and requests
class ServiceSubscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_subscriptions')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'service')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.service.name}"


class MessageRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_requests')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='message_requests')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message to {self.service.name} from {self.user.username}"


class CheckinRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkin_requests')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='checkin_requests')
    notes = models.TextField(blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_checkins')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Check-in at {self.service.name} for {self.user.username}"
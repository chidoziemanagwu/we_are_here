# custom_admin.py
from django.contrib.admin import AdminSite

class DjangoAdminSite(AdminSite):
    site_header = 'We Are Here Django Administration'
    site_title = 'We Are Here Django Admin'
    index_title = 'Django Admin Dashboard'

# Create an instance of the custom admin site
django_admin_site = DjangoAdminSite(name='django_admin')
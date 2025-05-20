from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from core.models import ServiceCategory, DemographicTag, Category

class Command(BaseCommand):
    help = 'Sets up initial admin user and basic data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up admin user...')

        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            with transaction.atomic():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@wearehere.org',
                    password='WeAreHere2024!'
                )
                self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
                self.stdout.write('Username: admin')
                self.stdout.write('Password: WeAreHere2024!')
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists.'))

        # Create basic categories if they don't exist
        self.create_basic_categories()
        self.create_demographic_tags()

        self.stdout.write(self.style.SUCCESS('Setup completed successfully!'))

    def create_basic_categories(self):
        categories = [
            {
                'name': 'Shelter',
                'description': 'Emergency and temporary housing options',
                'icon': 'fa-home',
                'priority': 1,
                'color_code': '#FF5733'
            },
            {
                'name': 'Food',
                'description': 'Food banks, soup kitchens, and meal services',
                'icon': 'fa-utensils',
                'priority': 2,
                'color_code': '#33FF57'
            },
            {
                'name': 'Clothing',
                'description': 'Free or low-cost clothing resources',
                'icon': 'fa-tshirt',
                'priority': 3,
                'color_code': '#3357FF'
            },
            {
                'name': 'Medical',
                'description': 'Healthcare services and clinics',
                'icon': 'fa-hospital',
                'priority': 4,
                'color_code': '#FF33F5'
            },
            {
                'name': 'Hygiene',
                'description': 'Shower facilities and hygiene supplies',
                'icon': 'fa-shower',
                'priority': 5,
                'color_code': '#33FFF5'
            },
            {
                'name': 'Legal',
                'description': 'Legal aid and advocacy services',
                'icon': 'fa-gavel',
                'priority': 6,
                'color_code': '#F5FF33'
            },
            {
                'name': 'Employment',
                'description': 'Job training and employment resources',
                'icon': 'fa-briefcase',
                'priority': 7,
                'color_code': '#FF8C33'
            }
        ]

        count = 0
        for cat_data in categories:
            cat, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'priority': cat_data['priority'],
                    'color_code': cat_data['color_code'],
                    'is_active': True,
                    'is_featured': True
                }
            )

            # Also create in Category model for compatibility
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'priority': cat_data['priority'],
                    'is_active': True,
                    'slug': cat.slug
                }
            )

            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {count} new service categories'))

    def create_demographic_tags(self):
        demographics = [
            {
                'name': 'Women Only',
                'description': 'Services specifically for women',
                'icon': 'fa-female',
                'badge_color': '#FF69B4'
            },
            {
                'name': 'Youth',
                'description': 'Services for youth and young adults',
                'icon': 'fa-child',
                'badge_color': '#32CD32'
            },
            {
                'name': 'LGBTQ+ Friendly',
                'description': 'Safe spaces for LGBTQ+ individuals',
                'icon': 'fa-rainbow',
                'badge_color': '#9B59B6'
            },
            {
                'name': 'Families',
                'description': 'Services for families with children',
                'icon': 'fa-users',
                'badge_color': '#3498DB'
            },
            {
                'name': 'Veterans',
                'description': 'Services for military veterans',
                'icon': 'fa-medal',
                'badge_color': '#2C3E50'
            },
            {
                'name': 'Seniors',
                'description': 'Services for older adults',
                'icon': 'fa-user-clock',
                'badge_color': '#E67E22'
            },
            {
                'name': 'Disability Accessible',
                'description': 'Services with accessibility accommodations',
                'icon': 'fa-wheelchair',
                'badge_color': '#1ABC9C'
            }
        ]

        count = 0
        for demo_data in demographics:
            _, created = DemographicTag.objects.get_or_create(
                name=demo_data['name'],
                defaults={
                    'description': demo_data['description'],
                    'icon': demo_data['icon'],
                    'badge_color': demo_data['badge_color'],
                    'is_active': True
                }
            )

            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {count} new demographic tags'))
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from core.models import Service, Category, DemographicTag

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'color_code']

class DemographicTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemographicTag
        fields = ['id', 'name', 'slug']

class ServiceSerializer(GeoFeatureModelSerializer):
    category = CategorySerializer(read_only=True)
    demographic_tags = DemographicTagSerializer(many=True, read_only=True)
    distance = serializers.FloatField(required=False)

    class Meta:
        model = Service
        geo_field = 'location'
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'phone', 'website', 'email', 'address',
            'opening_hours', 'is_active', 'capacity_status',
            'demographic_tags', 'distance'
        ]
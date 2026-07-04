from rest_framework import serializers
from .models import AnnotationImage, Polygon


class PolygonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Polygon
        fields = ['id', 'points', 'label', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']


class AnnotationImageSerializer(serializers.ModelSerializer):
    polygons = PolygonSerializer(many=True, read_only=True)

    class Meta:
        model = AnnotationImage
        fields = ['id', 'name', 'image', 'uploaded_at', 'polygons']
        read_only_fields = ['id', 'uploaded_at', 'polygons']

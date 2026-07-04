from django.contrib import admin
from .models import AnnotationImage, Polygon


@admin.register(AnnotationImage)
class AnnotationImageAdmin(admin.ModelAdmin):
    list_display  = ['name', 'user', 'uploaded_at']
    search_fields = ['name']


@admin.register(Polygon)
class PolygonAdmin(admin.ModelAdmin):
    list_display = ['label', 'color', 'image', 'created_at']

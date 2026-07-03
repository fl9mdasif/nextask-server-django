from django.db import models
from django.conf import settings


class AnnotationImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images')
    image       = models.ImageField(upload_to='annotations/')
    name        = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name


class Polygon(models.Model):
    image      = models.ForeignKey(AnnotationImage, on_delete=models.CASCADE, related_name='polygons')
    points     = models.JSONField()
    label      = models.CharField(max_length=100, blank=True)
    color      = models.CharField(max_length=20, default='#FF0000')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Polygon on {self.image.name}"
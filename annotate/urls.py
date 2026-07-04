from django.urls import path
from . import views

urlpatterns = [
    # Image endpoints
    path('images/',             views.image_list,    name='image-list'),
    path('images/<int:pk>/',    views.image_detail,  name='image-detail'),

    # Polygon endpoints
    path('images/<int:pk>/polygons/', views.polygon_list,   name='polygon-list'),
    path('polygons/<int:pk>/',        views.polygon_detail, name='polygon-detail'),
]
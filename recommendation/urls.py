from django.urls import path
from .views import top_products_view
from . import views

urlpatterns = [
    path('top-products/', views.top_products_view, name='top-products'),
    path('collaborative-filtering/', views.collaborative_filtering_view, name='collaborative-filtering'),
    path('pb/', views.recommendation_based_on_product_view, name='pb'),
]

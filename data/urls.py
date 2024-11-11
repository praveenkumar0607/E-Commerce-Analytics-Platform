from django.urls import path
from . import views
# from .views import UploadOrderDetailsView,upload_page
from django.urls import path
from .views import upload_page

from data.views import UploadOrderDetailsView

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import OrderDetailsViewSet

# router = DefaultRouter()
# router.register(r'orderdetails', OrderDetailsViewSet, basename='orderdetails')  # Ensure basename matches if specified
from .views import UserOrderDetailsAPIView



from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)





urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('api/', UserOrderDetailsAPIView.as_view(), name='api'),
    # path('api/', include(router.urls)),
    path('upload/',views.Dataupload,name='upload'),
    path('manipulation/',views.DataManipulation,name='manipulation'),
    path('visualization/',views.DataVisualization,name='visualization'),
    path('selecttable/', views.select_table, name='selecttable'),
    path('analyzetable/<str:table_name>/', views.analyze_table, name='analyzetable'),
    path('dataupload/',views.DataUpload,name='dataupload'),
    path('userdata/', views.user_data_list, name='userdata'),
    path('analyzeuserdata/', views.analyze_user_data, name='analyzeuserdata'),

    # path('uploadorderdetails/', UploadOrderDetailsView.as_view(), name='uploadorderdetails'),
    # path('uploadpage/', views.upload_page, name='uploadpage'),

    path('grafana_dashboard/<str:table_name>/', views.grafana_dashboard, name='grafana_dashboard'),


]



# urlpatterns = [
#     path('upload/', views.upload_page, name='upload'),
#     path('manipulation/', views.DataManipulation, name='manipulation'),
#     path('visualization/', views.DataVisualization, name='visualization'),
#     path('selecttable/', views.select_table, name='selecttable'),
#     path('analyzetable/<str:table_name>/', views.analyze_table, name='analyzetable'),
#     path('uploadorderdetails/', UploadOrderDetailsView.as_view(), name='uploadorderdetails'),
#     path('uploadpage/', views.upload_page, name='uploadpage'),
# ]





    

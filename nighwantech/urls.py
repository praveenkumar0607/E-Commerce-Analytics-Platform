"""
URL configuration for nighwantech project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path,include
from django.conf import settings
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView


admin.site.site_header='Nighwan Tech Pvt Ltd'
admin.site.site_title="NighwanTechAdmin"
admin.site.index_title='NighwanTechAdmin'

from adminuser import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    #  path('logout/', LogoutView.as_view(next_page='/admin/login/'), name='logout'),
    # path('logout/',RedirectView.as_view(url='/admin/logout/'),name='logout'),
    path('admin/adminuser/mymodel/', views.custom_change_list, name='custom_change_list'),
    path('admin/adminuser/mymodel/custom-change-list/', views.custom_change_list, name='custom_change_list'),
    path('admin/adminuser/mymodel/custom-page-2/', views.custom_page_2, name='custom_page_2'),
    path('admin/adminuser/mymodel/custom-page-3/', views.custom_page_3, name='custom_page_3'),
    path('', include('recommendation.urls')),
   
   
   
    path('',include('authentication.urls')),
    path('data/',include('data.urls')),
    path('csv/', include('csvdata.urls')),
    path('', include('django_prometheus.urls')),
    path('dataclean/',include('dataclean.urls')),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 # path('adminuser/',include('adminuser.urls')),

# 
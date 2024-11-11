from django.urls import path
from . import views

urlpatterns = [
    path('fillnull/', views.FillNull, name='fillnull'),
    path('cleaneddata/', views.cleaned_data, name='cleaneddata'),
    path('csv-files/', views.list_csv_files, name='list-csv-files'),
    path('viewdatainfo/', views.ViewDataInfo, name='viewdatainfo'),
    path('clean-csv-file/', views.cleandata, name='clean-csv-file'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('uploadcsv/', views.upload_file, name='uploadcsv'),
    # path('listfiles/', views.list_files, name='listfiles'),
    path('linkstable/', views.links_table, name='linkstable'),    
    # path('listfiles/', views.list_files, name='listfiles'),
    # path('uploaddata/', views.upload_data, name='uploaddata'),

    path('listfiles/', views.list_files, name='listfiles'),
    path('uploaddata/', views.upload_data, name='uploaddata'),
    path('listfilesanalysis/',views.list_files_analysis,name='listfilesanalysis'),
    path('analyzedata/',views.analyze_data,name='analyzedata'),



    path('listcsvfiles/', views.list_csvfiles, name='listcsvfiles'),
    path('createcsvtable/', views.create_csvtable, name='createcsvtable'),
    path('listcsvtables/', views.list_csvtables, name='listcsvtables'),
    path('deletecsvtable/<int:table_id>/', views.delete_csvtable, name='deletecsvtable'),



]

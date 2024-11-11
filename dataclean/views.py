from django.shortcuts import render, redirect
from django.conf import settings
import os
from .datacleanclass import DataCleaner
from django.contrib.auth.decorators import login_required

@login_required
def FillNull(request):
    return render(request, 'dataclean/fillnull.html')

@login_required
def list_csv_files(request):
    media_path = settings.MEDIA_ROOT
    csv_files = []
    for root, dirs, files in os.walk(media_path):
        for file in files:
            if file.endswith(".csv"):
                relative_path = os.path.relpath(os.path.join(root, file), media_path)
                csv_files.append({'name': file, 'path': relative_path})
    return {'files': csv_files}

@login_required
def cleaned_data(request):
    context = list_csv_files(request)
    return render(request, 'dataclean/cleaned_data.html', context)

@login_required
def cleandata(request):
    if request.method == 'POST':
        file_path = request.POST.get('csv_file')
        if file_path:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            cleaner = DataCleaner(full_path)
            print(f"DataFrame shape before cleaning: {cleaner.df.shape}")
            cleaner.clean_data()
            print(f"DataFrame shape after cleaning: {cleaner.df.shape}")
            message = "Cleaning successful!"
            context = list_csv_files(request)
            context['message'] = message
            return render(request, 'dataclean/cleaned_data.html', context)
    return redirect('cleaneddata')

@login_required
def ViewDataInfo(request):
    media_path = settings.MEDIA_ROOT
    csv_files = []
    for root, dirs, files in os.walk(media_path):
        for file in files:
            if file.endswith(".csv"):
                relative_path = os.path.relpath(os.path.join(root, file), media_path)
                csv_files.append({'name': file, 'path': relative_path})

    if request.method == 'POST':
        file_path = request.POST.get('csv_file')
        if file_path:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            cleaner = DataCleaner(full_path)
            info = cleaner.DataInfo()
            return render(request, 'dataclean/datainfo.html', {'info': info, 'files': csv_files})

    return render(request, 'dataclean/datainfo.html', {'files': csv_files})
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

superuser_required = user_passes_test(lambda u: u.is_superuser)

# @superuser_required
# def custompage(request):
#     return render(request, 'custom_page.html')



# myapp/views.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

# @staff_member_required
# def custom_change_list(request):
#     return render(request, 'admin/adminuser/mymodel/change_list.html')











# adminuser/views.py

# from django.shortcuts import render
# from .models import MyModel

# def custom_model_page(request):
#     instances = MyModel.objects.all()
#     return render(request, 'custom_model_page.html', {'instances': instances})








from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def custom_change_list(request):
    
    return render(request, 'admin/adminuser/mymodel/custom_change_list.html')


from csvdata.models import UserDataFile
@staff_member_required

@staff_member_required
def custom_page_2(request):
    # Retrieve all UserDataFile instances
    user_files = UserDataFile.objects.all()

    # Pass the retrieved files to the template
    context = {
        'user_files': user_files
    }

    return render(request, 'admin/adminuser/mymodel/custom_page_2.html', context)


@staff_member_required
def custom_page_3(request):
    return render(request, 'admin/adminuser/mymodel/custom_page_3.html')

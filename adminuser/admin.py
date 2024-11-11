# # myapp/admin.py

# from django.contrib import admin
# from .models import MyModel
# from django.contrib import admin
# from .models import MyModel
# from django.urls import path
# from django.shortcuts import redirect
# from django.shortcuts import render
# from django.urls import reverse

# @admin.register(MyModel)
# class MyModelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     # change_list_template = "admin/adminuser/mymodel/change_list.html"
#     def changelist_view(self, request, extra_context=None):
#         return redirect(reverse('custom_change_list'))

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('custom-change-list/', self.admin_site.admin_view(self.custom_change_list), name='custom_change_list')
#         ]
#         return custom_urls + urls

#     def custom_change_list(self, request):
#         return render(request, 'admin/adminuser/mymodel/change_list.html')

# # admin.site.register(MyModel, MyModelAdmin)



# # adminuser/admin.py

# # from django.contrib import admin
# # from .models import MyModel

# # @admin.register(MyModel)
# # class MyModelAdmin(admin.ModelAdmin):
# #     list_display = ('name', 'description')  # Display fields in the admin list view




from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import MyModel

# @admin.register(MyModel)
# class MyModelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     change_list_template = "admin/adminuser/mymodel/change_list.html"
    
#     def changelist_view(self, request, extra_context=None):
#         return redirect(reverse('admin:custom_change_list'))

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('custom-change-list/', self.admin_site.admin_view(self.custom_change_list), name='custom_change_list')
#         ]
#         return custom_urls + urls

#     def custom_change_list(self, request):
#         return render(request, 'admin/adminuser/mymodel/change_list.html')



# from django.contrib import admin
# from django.urls import path
# from django.shortcuts import redirect, render
# from django.urls import reverse
# from .models import MyModel

# @admin.register(MyModel)
# class MyModelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     change_list_template = "admin/adminuser/mymodel/change_list.html"
    
#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['custom_data'] = 'Your custom data'
#         return super().changelist_view(request, extra_context=extra_context)

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('custom-change-list/', self.admin_site.admin_view(self.custom_change_list), name='custom_change_list')
#         ]
#         return custom_urls + urls

#     def custom_change_list(self, request):
#         return render(request, 'admin/adminuser/mymodel/change_list.html')


from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect
from .models import MyModel

# @admin.register(MyModel)
# class MyModelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     change_list_template = "admin/adminuser/mymodel/change_list.html"

#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['custom_data'] = 'Your custom data'
#         return super().changelist_view(request, extra_context=extra_context)

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('custom-change-list/', self.admin_site.admin_view(self.custom_change_list), name='custom_change_list')
#         ]
#         return custom_urls + urls

#     def custom_change_list(self, request):
#         context = dict(
#             self.admin_site.each_context(request),
#             custom_data='Your custom data',
#             opts=self.model._meta,
#         )
#         return render(request, 'admin/adminuser/mymodel/change_list.html', context)



from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import MyModel

# @admin.register(MyModel)
# class MyModelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('custom-change-list/', self.admin_site.admin_view(self.custom_change_list), name='custom_change_list'),
#             path('custom-page-2/', self.admin_site.admin_view(self.custom_page_2), name='custom_page_2'),
#             path('custom-page-3/', self.admin_site.admin_view(self.custom_page_3), name='custom_page_3'),
#         ]
#         return custom_urls + urls

#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['custom_urls'] = [
#             {'url': reverse('admin:custom_change_list'), 'name': 'Custom Change List'},
#             {'url': reverse('admin:custom_page_2'), 'name': 'Custom Page 2'},
#             {'url': reverse('admin:custom_page_3'), 'name': 'Custom Page 3'},
#         ]
#         return super().changelist_view(request, extra_context=extra_context)

#     def custom_change_list(self, request):
#         return render(request, 'admin/adminuser/mymodel/custom_change_list.html')

#     def custom_page_2(self, request):
#         return render(request, 'admin/adminuser/mymodel/custom_page_2.html')

#     def custom_page_3(self, request):
#         return render(request, 'admin/adminuser/mymodel/custom_page_3.html')
from csvdata.models import UserDataFile

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom-change-list/', self.admin_site.admin_view(self.custom_change_list), name='custom_change_list'),
            path('custom-page-2/', self.admin_site.admin_view(self.custom_page_2), name='custom_page_2'),
            path('custom-page-3/', self.admin_site.admin_view(self.custom_page_3), name='custom_page_3'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_urls'] = [
            {'url': reverse('admin:custom_change_list'), 'name': 'Custom Change List'},
            {'url': reverse('admin:custom_page_2'), 'name': 'Custom Page 2'},
            {'url': reverse('admin:custom_page_3'), 'name': 'Custom Page 3'},
        ]
        return super().changelist_view(request, extra_context=extra_context)

    def custom_change_list(self, request):
        django_quotes = [
            "Django makes it easier to build web applications.",
            "Django is a high-level Python web framework.",
            "Django encourages rapid development and clean, pragmatic design.",
            "With Django, you can take Web applications from concept to launch in a matter of hours.",
            "Django follows the 'batteries-included' philosophy.",
            "Django is designed to help developers take applications from concept to completion as quickly as possible.",
            "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.",
            "Django takes care of much of the hassle of web development.",
            "Django's primary goal is to ease the creation of complex, database-driven websites.",
            "Django emphasizes reusability and 'pluggability' of components.",
            "Less code, fewer bugs.",
            "Django is a free and open-source web framework.",
            "Django has a thriving and active community.",
            "Django helps you write software that is easier to maintain and extend.",
            "Django uses Python, which is one of the most popular programming languages.",
            "Django has a lot of built-in features for security.",
            "Django is flexible and scalable.",
            "Django provides an admin interface that is very easy to customize.",
            "Django supports rapid prototyping and production-ready solutions.",
            "Django's ORM is one of its best features.",
            "Django's templating engine is powerful and easy to use.",
            "Django has excellent documentation.",
            "Django helps you build better web applications faster.",
            "Django abstracts many common web development tasks.",
            "Django is built by experienced developers to handle complex web applications.",
            "Django is perfect for getting started with web development.",
            "Django’s user authentication system is highly customizable.",
            "Django allows you to develop your web applications quickly.",
            "Django is known for its simplicity and flexibility.",
            "Django helps developers avoid common security mistakes."
        ]

        ai_paragraphs = [
            "Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior. It involves the development of algorithms that allow computers to perform tasks that would normally require human intelligence, such as visual perception, speech recognition, decision-making, and language translation.",
            "Data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data. It combines various disciplines such as statistics, data analysis, machine learning, and big data to analyze and interpret complex data.",
            "Machine learning is a subset of AI that involves the use of algorithms and statistical models to enable computers to improve their performance on a task through experience. Machine learning algorithms build a mathematical model based on sample data, known as 'training data,' in order to make predictions or decisions without being explicitly programmed to perform the task.",
            "AI has the potential to revolutionize various industries, including healthcare, finance, education, and transportation. For example, AI-powered systems can assist doctors in diagnosing diseases, predict stock market trends, personalize learning experiences for students, and optimize traffic flow in cities.",
            "Data science plays a crucial role in the development of AI and machine learning applications. By analyzing large datasets, data scientists can identify patterns and trends that can be used to train machine learning models and make data-driven decisions.",
            "The integration of AI and data science has led to significant advancements in fields such as natural language processing, computer vision, and robotics. These technologies have enabled the development of innovative applications such as virtual assistants, autonomous vehicles, and smart home devices."
        ]

        context = {
            'django_quotes': django_quotes,
            'ai_paragraph_1': ai_paragraphs[0],
            'ai_paragraph_2': ai_paragraphs[1],
            'ai_paragraph_3': ai_paragraphs[2],
            'ai_paragraph_4': ai_paragraphs[3],
            'ai_paragraph_5': ai_paragraphs[4],
            'ai_paragraph_6': ai_paragraphs[5],
        }
        return render(request, 'admin/adminuser/mymodel/custom_change_list.html', context)

    def custom_page_2(self, request):
        files = UserDataFile.objects.all()
        context = {
            'files': files,
        }

        return render(request, 'admin/adminuser/mymodel/custom_page_2.html',context)

    def custom_page_3(self, request):
        return render(request, 'admin/adminuser/mymodel/custom_page_3.html')

from django.contrib import admin
from .models import UserTable,UserDataFile



# Register your models here.
def get_all_field_names(model):
    return [field.name for field in model._meta.get_fields() if not (field.many_to_many or field.one_to_many)]



class UserTableAdmin(admin.ModelAdmin):
    list_display = get_all_field_names(UserTable)


class UserDataFileAdmin(admin.ModelAdmin):
    list_display = get_all_field_names(UserDataFile)



admin.site.register(UserTable, UserTableAdmin)
admin.site.register(UserDataFile, UserDataFileAdmin)

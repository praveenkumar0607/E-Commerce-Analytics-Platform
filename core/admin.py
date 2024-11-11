
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('id','email', 'name','username','tc' ,'is_staff', 'is_active', 'created_at', 'updated_at')
    search_fields = ('email', 'name')
    ordering=('email','id')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal=()

    fieldsets = (
        ('USer Credentials', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'tc')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'tc', 'password1', 'password2'),
        }),
    )

    # Corrected list_filter to refer to is_active and is_superuser
    list_filter = ('is_active', 'is_superuser')

# Register your User model with the CustomUserAdmin
admin.site.register(User, UserAdmin)


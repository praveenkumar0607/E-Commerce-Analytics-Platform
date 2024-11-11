
from django.contrib import admin
from .models import OrderDetails,UserTable,UserOrder
from django.contrib import admin
from .models import OrderDetails, UserOrder

def get_all_field_names(model):
    return [field.name for field in model._meta.get_fields() if not (field.many_to_many or field.one_to_many)]

class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = get_all_field_names(OrderDetails)

class UserOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'order_details', 'created_at']

admin.site.register(OrderDetails, OrderDetailsAdmin)
admin.site.register(UserOrder, UserOrderAdmin)

admin.site.register(UserTable)
from django.db import models
from django.conf import settings
import pandas as pd
import uuid
from datetime import datetime
from django.apps import apps



# Create your models here.

class OrderDetails(models.Model):

    Type = models.CharField(max_length=255)
    Days_for_shipping_real = models.IntegerField()
    Days_for_shipment_scheduled = models.IntegerField()
    Benefit_per_order = models.FloatField()
    Sales_per_customer = models.FloatField()
    Delivery_Status = models.CharField(max_length=255)
    Late_delivery_risk = models.IntegerField()

    Category_Id = models.IntegerField()
    Category_Name = models.CharField(max_length=255)
    Customer_City = models.CharField(max_length=255)
    Customer_Country = models.CharField(max_length=255)
    Customer_Email = models.EmailField()
    Customer_Fname = models.CharField(max_length=255)
    Customer_Id = models.IntegerField()
    Customer_Lname = models.CharField(max_length=255)
    Customer_Password = models.CharField(max_length=255)
    Customer_Segment = models.CharField(max_length=255)
    Customer_State = models.CharField(max_length=255)
    Customer_Street = models.CharField(max_length=255)
    Customer_Zipcode = models.FloatField(null=True)
    
    Department_Id = models.IntegerField()
    Department_Name = models.CharField(max_length=255)
    
    Latitude = models.FloatField()
    Longitude = models.FloatField()
    Market = models.CharField(max_length=255)
    
    Order_City = models.CharField(max_length=255)
    Order_Country = models.CharField(max_length=255, null=True)
    Order_Customer_Id = models.FloatField(null=True)
    order_date_DateOrders = models.CharField(max_length=255, null=True)
    Order_Id = models.FloatField(null=True)
    Order_Item_Cardprod_Id = models.FloatField(null=True)
    Order_Item_Discount = models.FloatField(null=True)
    Order_Item_Discount_Rate = models.FloatField(null=True)
    Order_Item_Id = models.FloatField(null=True)
    Order_Item_Product_Price = models.FloatField(null=True)
    Order_Item_Profit_Ratio = models.FloatField(null=True)
    Order_Item_Quantity = models.FloatField(null=True)
    
    Sales = models.FloatField(null=True)
    Order_Item_Total = models.FloatField(null=True)
    Order_Profit_Per_Order = models.FloatField(null=True)
    Order_Region = models.CharField(max_length=255, null=True)
    Order_State = models.CharField(max_length=255, null=True)
    Order_Status = models.CharField(max_length=255, null=True)
    Order_Zipcode = models.FloatField(null=True, blank=True)
    
    Product_Card_Id = models.FloatField(null=True)
    Product_Category_Id = models.FloatField(null=True)
    Product_Description = models.TextField(null=True, blank=True)
    Product_Image = models.CharField(max_length=255, null=True)
    Product_Name = models.CharField(max_length=255, null=True)
    Product_Price = models.FloatField(null=True)
    Product_Status = models.FloatField(null=True)
    
    shipping_date_DateOrders = models.CharField(max_length=255, null=True)
    Shipping_Mode = models.CharField(max_length=255, null=True)
    
    tablename = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', default=None)

    def str(self):
        return f"Order {self.Order_Id}"



class UserOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='+', default=None)
    order_details = models.ForeignKey(OrderDetails, on_delete=models.CASCADE,related_name='+', default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user.name} - Order {self.order_details.Order_Id}"






class UserTable(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    table_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.table_name

# Function to create a dynamic model
def create_dynamic_model(model_name, fields):
    model_name = model_name.replace("-", "_").replace(".", "_")
    attrs = {'__module__': 'data.models'}
    for field_name, field_type in fields.items():
        attrs[field_name] = field_type
    return type(model_name, (models.Model,), attrs)


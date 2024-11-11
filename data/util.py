from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from core.models import User
from .models import OrderDetails
from .import validate
import pandas as pd

@login_required
def DataUpload(request):
    required_columns = [
        'Type',
        'Days_for_shipping_real',
        'Days_for_shipment_scheduled',
        'Benefit_per_order',
        'Sales_per_customer',
        'Delivery_Status',
        'Late_delivery_risk',
        'Category_Id',
        'Category_Name',
        'Customer_City',
        'Customer_Country',
        'Customer_Email',
        'Customer_Fname',
        'Customer_Id',
        'Customer_Lname',
        'Customer_Password',
        'Customer_Segment',
        'Customer_State',
        'Customer_Street',
        'Customer_Zipcode',
        'Department_Id',
        'Department_Name',
        'Latitude',
        'Longitude',
        'Market',
        'Order_City',
        'Order_Country',
        'Order_Customer_Id',
        'order_date_DateOrders',
        'Order_Id',
        'Order_Item_Cardprod_Id',
        'Order_Item_Discount',
        'Order_Item_Discount_Rate',
        'Order_Item_Id',
        'Order_Item_Product_Price',
        'Order_Item_Profit_Ratio',
        'Order_Item_Quantity',
        'Sales',
        'Order_Item_Total',
        'Order_Profit_Per_Order',
        'Order_Region',
        'Order_State',
        'Order_Status',
        'Order_Zipcode',
        'Product_Card_Id',
        'Product_Category_Id',
        'Product_Description',
        'Product_Image',
        'Product_Name',
        'Product_Price',
        'Product_Status',
        'shipping_date_DateOrders',
        'Shipping_Mode',
    ]

    if request.method == 'POST':
        user_email = request.user.email  # Accessing user email
        file = request.FILES.get('file')

        if not file:
            messages.error(request, "No file uploaded.")
            return redirect('home')

        try:
            validate.validate_file_extension(file)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('home')

        try:
            csvfile = validate.validate_csv_file(file)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('home')

        try:
            user = User.objects.filter(email=user_email).first()  # Get user by email
            if user:
                filename = file.name.split('.')[0]
                df = pd.read_csv(csvfile)

                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f"Missing columns in CSV: {', '.join(missing_columns)}")
                    return redirect('home')

                tablename = f"data_{user_email.replace('@', '_').replace('.', '_')}"
                records = []
                for index, row in df.iterrows():
                    record = OrderDetails(
                        Type=row['Type'],
                        Days_for_shipping_real=row['Days_for_shipping_real'],
                        Days_for_shipment_scheduled=row['Days_for_shipment_scheduled'],
                        Benefit_per_order=row['Benefit_per_order'],
                        Sales_per_customer=row['Sales_per_customer'],
                        Delivery_Status=row['Delivery_Status'],
                        Late_delivery_risk=row['Late_delivery_risk'],
                        Category_Id=row['Category_Id'],
                        Category_Name=row['Category_Name'],
                        Customer_City=row['Customer_City'],
                        Customer_Country=row['Customer_Country'],
                        Customer_Email=row['Customer_Email'],
                        Customer_Fname=row['Customer_Fname'],
                        Customer_Id=row['Customer_Id'],
                        Customer_Lname=row['Customer_Lname'],
                        Customer_Password=row['Customer_Password'],
                        Customer_Segment=row['Customer_Segment'],
                        Customer_State=row['Customer_State'],
                        Customer_Street=row['Customer_Street'],
                        Customer_Zipcode=row['Customer_Zipcode'],
                        Department_Id=row['Department_Id'],
                        Department_Name=row['Department_Name'],
                        Latitude=row['Latitude'],
                        Longitude=row['Longitude'],
                        Market=row['Market'],
                        Order_City=row['Order_City'],
                        Order_Country=row['Order_Country'],
                        Order_Customer_Id=row['Order_Customer_Id'],
                        order_date_DateOrders=row['order_date_DateOrders'],
                        Order_Id=row['Order_Id'],
                        Order_Item_Cardprod_Id=row['Order_Item_Cardprod_Id'],
                        Order_Item_Discount=row['Order_Item_Discount'],
                        Order_Item_Discount_Rate=row['Order_Item_Discount_Rate'],
                        Order_Item_Id=row['Order_Item_Id'],
                        Order_Item_Product_Price=row['Order_Item_Product_Price'],
                        Order_Item_Profit_Ratio=row['Order_Item_Profit_Ratio'],
                        Order_Item_Quantity=row['Order_Item_Quantity'],
                        Sales=row['Sales'],
                        Order_Item_Total=row['Order_Item_Total'],
                        Order_Profit_Per_Order=row['Order_Profit_Per_Order'],
                        Order_Region=row['Order_Region'],
                        Order_State=row['Order_State'],
                        Order_Status=row['Order_Status'],
                        Order_Zipcode=row['Order_Zipcode'],
                        Product_Card_Id=row['Product_Card_Id'],
                        Product_Category_Id=row['Product_Category_Id'],
                        Product_Description=row['Product_Description'],
                        Product_Image=row['Product_Image'],
                        Product_Name=row['Product_Name'],
                        Product_Price=row['Product_Price'],
                        Product_Status=row['Product_Status'],
                        shipping_date_DateOrders=row['shipping_date_DateOrders'],
                        Shipping_Mode=row['Shipping_Mode'],
                        tablename=tablename,
                        user=user
                    )
                    records.append(record)

                OrderDetails.objects.bulk_create(records)
                messages.success(request, 'File uploaded successfully.')
            else:
                messages.error(request, 'User does not exist')
        except Exception as e:
            messages.error(request, f'Something went wrong: {str(e)}')
            return redirect('home')

    return render(request, 'data/data.html')

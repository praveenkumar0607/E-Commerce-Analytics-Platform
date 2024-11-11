from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.conf import settings
import os
import pandas as pd
from django.contrib import messages
from .forms import UserFileForm, UserTableForm
from .models import UserDataFile, UserTable
from data.models import OrderDetails  # Adjust this import based on your actual app name
from django.db import connection




@login_required
def upload_file(request):
    user_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', str(request.user.id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    if request.method == 'POST':
        form = UserFileForm(request.POST, request.FILES)
        if form.is_valid():
            user_file = form.save(commit=False)
            user_file.user = request.user
            user_file.save()
            return HttpResponseRedirect('/csv/listfiles/')
    else:
        form = UserFileForm()

    return render(request, 'datacsv/upload.html', {'form': form})

# @login_required
# def list_files(request):
#     files = UserDataFile.objects.filter(user=request.user)
#     return render(request, 'datacsv/files.html', {'files': files})

@login_required
def links_table(request):
    return render(request, 'datacsv/linkstable.html')





@login_required
def list_files(request):
    files = UserDataFile.objects.filter(user=request.user)
    return render(request, 'datacsv/listfiles.html', {'files': files})
# views.py

@login_required
def list_files_analysis(request):
    files = UserDataFile.objects.filter(user=request.user)
    return render(request, 'datacsv/listfileanalysis.html', {'files': files})

@login_required
def analyze_data(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        if not file_id:
            messages.error(request, "No file selected.")
            return redirect('listfilesanalysis')

        try:
            user_file = UserDataFile.objects.get(id=file_id, user=request.user)
            df = pd.read_csv(user_file.file.path)
            columns_summary = df.describe().to_html()  # Generate HTML summary of columns
            columns_list = df.columns.tolist()  # Get list of columns

            return render(request, 'datacsv/analysis_result.html', {
                'file_name': user_file.file.name,
                'columns_summary': columns_summary,
                'columns_list': columns_list
            })

        except UserDataFile.DoesNotExist:
            messages.error(request, "File not found.")
            return redirect('listfilesanalysis')
        except Exception as e:
            messages.error(request, f"Error analyzing data: {str(e)}")
            return redirect('listfilesanalysis')

    return redirect('listfilesanalysis')











@login_required
def list_csvfiles(request):
    files = UserDataFile.objects.filter(user=request.user)
    return render(request, 'datacsv/listcsvfiles.html', {'files': files})



import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db import connection, IntegrityError
from .forms import UserTableForm
from .models import UserDataFile, UserTable

from django.contrib import messages
from django.db import IntegrityError, connection
from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import pandas as pd
from .forms import UserTableForm
from .models import UserDataFile, UserTable

@login_required
def create_csvtable(request):
    if request.method == 'POST':
        form = UserTableForm(request.POST)
        if form.is_valid():
            file_id = form.cleaned_data['file'].id
            table_name = form.cleaned_data['table_name']
            user_table = form.save(commit=False)
            user_table.user = request.user

            # Get the selected file
            user_file = get_object_or_404(UserDataFile, id=file_id, user=request.user)
            file_path = user_file.file.path
            df = pd.read_csv(file_path)

            # Generate a unique table name
            unique_table_name = f"{table_name}_{request.user.username}_{user_file.id}"

            with connection.cursor() as cursor:
                # Check if table already exists
                cursor.execute("SHOW TABLES LIKE %s", [unique_table_name])
                if cursor.fetchone():
                    # If table exists, prompt user to choose a different name
                    messages.error(request, 'Table with this name already exists. Please choose a different name.')
                else:
                    # Create the table dynamically with the unique name
                    columns = df.columns
                    try:
                        cursor.execute(f'CREATE TABLE `{unique_table_name}` (id INT AUTO_INCREMENT PRIMARY KEY)')
                        for column in columns:
                            cursor.execute(f'ALTER TABLE `{unique_table_name}` ADD COLUMN `{column}` VARCHAR(255)')

                        # Insert data into the table
                        for _, row in df.iterrows():
                            placeholders = ', '.join(['%s'] * len(row))
                            sql = f'INSERT INTO `{unique_table_name}` ({", ".join([f"`{col}`" for col in columns])}) VALUES ({placeholders})'
                            cursor.execute(sql, tuple(row))

                        user_table.table_name = unique_table_name
                        user_table.save()

                        messages.success(request, 'Table created successfully.')
                        return HttpResponseRedirect('/csv/listcsvtables/')
                    except IntegrityError:
                        messages.error(request, 'An error occurred while creating the table. Please try again.')
    else:
        form = UserTableForm()
        form.fields['file'].queryset = UserDataFile.objects.filter(user=request.user)

    return render(request, 'datacsv/createcsvtable.html', {'form': form})

@login_required
def list_csvtables(request):
    tables = UserTable.objects.filter(user=request.user)
    return render(request, 'datacsv/listcsvtables.html', {'tables': tables})

@login_required
def delete_csvtable(request, table_id):
    user_table = get_object_or_404(UserTable, id=table_id, user=request.user)
    table_name = user_table.table_name

    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE `{table_name}`")

    user_table.delete()
    return HttpResponseRedirect('/csv/listcsvtables/')










@login_required
def upload_data(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        if not file_id:
            messages.error(request, "No file selected.")
            return redirect('listfiles')

        user_file = UserDataFile.objects.get(id=file_id, user=request.user)
        if not user_file:
            messages.error(request, "File not found.")
            return redirect('listfiles')

        try:
            df = pd.read_csv(user_file.file.path)
        except Exception as e:
            messages.error(request, f"Error reading CSV file: {str(e)}")
            return redirect('listfiles')

        required_columns = [
            'Type', 'Days_for_shipping_real', 'Days_for_shipment_scheduled', 'Benefit_per_order',
            'Sales_per_customer', 'Delivery_Status', 'Late_delivery_risk', 'Category_Id',
            'Category_Name', 'Customer_City', 'Customer_Country', 'Customer_Email', 'Customer_Fname',
            'Customer_Id', 'Customer_Lname', 'Customer_Password', 'Customer_Segment', 'Customer_State',
            'Customer_Street', 'Customer_Zipcode', 'Department_Id', 'Department_Name', 'Latitude',
            'Longitude', 'Market', 'Order_City', 'Order_Country', 'Order_Customer_Id', 'order_date_DateOrders',
            'Order_Id', 'Order_Item_Cardprod_Id', 'Order_Item_Discount', 'Order_Item_Discount_Rate',
            'Order_Item_Id', 'Order_Item_Product_Price', 'Order_Item_Profit_Ratio', 'Order_Item_Quantity',
            'Sales', 'Order_Item_Total', 'Order_Profit_Per_Order', 'Order_Region', 'Order_State',
            'Order_Status', 'Order_Zipcode', 'Product_Card_Id', 'Product_Category_Id', 'Product_Description',
            'Product_Image', 'Product_Name', 'Product_Price', 'Product_Status', 'shipping_date_DateOrders',
            'Shipping_Mode'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            messages.error(request, f"Missing columns in CSV: {', '.join(missing_columns)}")
            return redirect('listfiles')

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
                tablename=f"data_{request.user.email.replace('@', '_').replace('.', '_')}",
                user=request.user
            )
            records.append(record)

        try:
            OrderDetails.objects.bulk_create(records)
            messages.success(request, 'File uploaded successfully.')
        except Exception as e:
            messages.error(request, f"Error saving data: {str(e)}")

        return redirect('listfiles')

    return redirect('listfiles')



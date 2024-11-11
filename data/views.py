from django.apps import apps
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import pandas as pd
import uuid
from datetime import datetime
import logging
from .models import UserTable, create_dynamic_model, OrderDetails, UserOrder
from django.db import connection, IntegrityError, models
from django.conf import settings
from django.core.management import call_command
from django.contrib import messages
from django.core.exceptions import ValidationError
from core.models import User
from .import validate
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderDetailsSerializer
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.db.models import Avg

logger = logging.getLogger(__name__)






@login_required
def Dataupload(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        user_email = request.user.email
        table_name = request.POST.get('table_name')  # Get table_name input
        
        try:
            # Read CSV and create dynamic model
            table_name, dynamic_model, df = read_csv_and_create_model(user_email, csv_file, table_name)
            
            # Save the table name in UserTable
            user_table, created = UserTable.objects.get_or_create(user=request.user, table_name=table_name)
            
            # Insert data into the dynamic table
            for _, row in df.iterrows():
                dynamic_instance = dynamic_model(**row.to_dict())
                dynamic_instance.save()
            
            return JsonResponse({'status': 'success', 'message': 'CSV data stored successfully.'})
        
        except IntegrityError as e:
            logger.error(f'IntegrityError: {e}')
            return JsonResponse({'status': 'fail', 'message': f'IntegrityError: {str(e)}'})

        except Exception as e:
            logger.error(f'Error: {e}')
            return JsonResponse({'status': 'fail', 'message': f'Error: {str(e)}'})

    return render(request, 'data/dataupload.html')

def read_csv_and_create_model(user_email, csv_file, table_name):
    df = pd.read_csv(csv_file)
    
    # Check if 'id' column exists in the DataFrame
    if 'id' in df.columns:
        df.drop(columns=['id'], inplace=True)
    
    # Generate unique table name using timestamp and UUID
    unique_id = uuid.uuid4().hex[:8]  # Get first 8 characters of UUID
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # Current timestamp
    full_table_name = f"data_{user_email.replace('@', '_').replace('.', '_')}_{table_name}_{timestamp}_{unique_id}"
    
    # Create fields dictionary
    fields = {col: models.CharField(max_length=255) for col in df.columns}
    
    # Create dynamic model
    dynamic_model = create_dynamic_model(full_table_name, fields)
    
    # Create table in the database
    try:
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(dynamic_model)
        logging.info(f"Table {full_table_name} created successfully.")
    except Exception as e:
        logging.error(f"Error creating table {full_table_name}: {e}")
        raise
    
    return full_table_name, dynamic_model, df




@login_required
def analyze_table(request, table_name):
    try:
        # Dynamically load the model
        model = apps.get_model('data', table_name)
        if not model:
            raise LookupError(f"Table {table_name} not found.")

        queryset = model.objects.all()
        df = pd.DataFrame(list(queryset.values()))

        # Perform analysis
        null_values = df.isnull().sum()
        description = df.describe(include='all').transpose()  # Transpose for better readability
        summary_html = df.to_html(index=False)  # Convert DataFrame to HTML table

        # Log the table name and analysis results for debugging
        logging.info(f"Analyzing table: {table_name}")
        logging.info(f"Null values:\n{null_values}")
        logging.info(f"Description:\n{description}")

        return render(request, 'data/analyze_table.html', {
            'table_name': table_name,
            'null_values': null_values.to_dict(),
            'description': description.to_dict(),
            'summary_html': summary_html
        })

    except LookupError as e:
        logging.error(f"LookupError: {str(e)}")
        return JsonResponse({'status': 'fail', 'message': 'Table not found'})
    except Exception as e:
        logging.error(f"Error analyzing table {table_name}: {e}")
        return JsonResponse({'status': 'fail', 'message': f'Error: {str(e)}'})


# @login_required
# def select_table(request):
#     if request.method == 'POST':
#         table_name = request.POST.get('table_name')
#         return redirect('analyzetable', table_name=table_name)
    
#     user_tables = UserTable.objects.filter(user=request.user)
#     return render(request, 'data/select_table.html', {'user_tables': user_tables})


@login_required
def select_table(request):
    if request.method == 'POST':
        table_name = request.POST.get('table_name')
        user_email = request.user.email
        
        # Query to fetch user's data based on table name and email
        user_data = OrderDetails.objects.filter(user__email=user_email, tablename=table_name)
        
        # Pass user_data and table_name to the template for rendering
        return render(request, 'data/select_table.html', {'user_data': user_data, 'table_name': table_name})
    
    # Fetch all unique table names associated with the current user
    user_tables = OrderDetails.objects.filter(user=request.user).values_list('tablename', flat=True).distinct()
    
    return render(request, 'data/select_table.html', {'user_tables': user_tables})

# userdata/views.py

@login_required
def user_data_list(request):
    # Fetch all data entries for the currently logged-in user
    user_data_entries = OrderDetails.objects.filter(user=request.user).order_by('-id')

    # Pass the data entries to the template
    context = {
        'user_data_entries': user_data_entries
    }
    return render(request, 'data/user_data_list.html', context)

# views.py




@login_required
def analyze_user_data(request):
    # Fetch all data entries for the currently logged-in user
    user_data_entries = OrderDetails.objects.filter(user=request.user).order_by('-id')
    
    # Convert the queryset to a pandas DataFrame
    data = pd.DataFrame(list(user_data_entries.values()))
    
    if data.empty:
        # If the DataFrame is empty, set a message in the context and skip the analysis steps
        context = {
            'message': 'No data available for analysis.',
            'table_name': 'OrderDetails',  # You can change this dynamically if needed
        }
    else:
        # Perform various analyses
        columns_info = data.dtypes.to_dict()
        null_values = data.isnull().sum().to_dict()
        description = data.describe(include='all').to_dict()
        
        # Prepare a summary (optional)
        summary = data.describe().transpose().to_string()
        
        # Pass the analysis results to the template
        context = {
            'table_name': 'OrderDetails',  # You can change this dynamically if needed
            'columns_info': columns_info,
            'null_values': null_values,
            'description': description,
            'summary': summary  # Pass summary to template if needed
        }
    
    return render(request, 'data/analyze_user_data.html', context)




"""

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
                order_details_records = []
                user_order_records = []                
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
                for record in records:
                    UserOrder.objects.create(user=request.user, order_details=record)
                    

                messages.success(request, 'File uploaded successfully.')
            else:
                messages.error(request, 'User does not exist')
        except Exception as e:
            messages.error(request, f'Something went wrong: {str(e)}')
            return redirect('home')

    return render(request, 'data/data.html')

"""





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
                df = pd.read_csv(csvfile)

                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f"Missing columns in CSV: {', '.join(missing_columns)}")
                    return redirect('home')

                tablename = f"data_{user_email.replace('@', '_').replace('.', '_')}"
                order_details_records = []
                user_order_records = []

                for index, row in df.iterrows():
                    order_details = OrderDetails(
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
                    order_details.save()  # Save each OrderDetails instance
                    order_details_records.append(order_details)

                # Create UserOrder instances after saving OrderDetails
                for order_details in order_details_records:
                    user_order = UserOrder.objects.create(user=request.user, order_details=order_details)
                    user_order_records.append(user_order)

                messages.success(request, 'File uploaded successfully.')
            else:
                messages.error(request, 'User does not exist')
        except Exception as e:
            messages.error(request, f'Something went wrong: {str(e)}')
            return redirect('home')

    return render(request, 'data/data.html')























@login_required
class UploadOrderDetailsView(APIView):
    parser_classes = [FileUploadParser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'data/upload.html'

    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)    

    # @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return render(request, 'data/upload.html', {'error': 'No file provided'})

        file_obj = request.FILES['file']
        user_email = request.user.email
        tablename = f"data_{user_email.replace('@', '_').replace('.', '_')}"

        try:
            # Read the CSV file
            df = pd.read_csv(file_obj)

            # Validate and process the data
            instances = []
            for index, row in df.iterrows():
                data = row.to_dict()
                serializer = OrderDetailsSerializer(data=data)
                
                if serializer.is_valid():
                    instance = OrderDetails(**serializer.validated_data)
                    instance._meta.db_table = tablename  # Dynamically set the table name
                    instances.append(instance)
                else:
                    return render(request, 'data/upload.html', {'error': serializer.errors})

            # Bulk create instances
            OrderDetails.objects.bulk_create(instances)

            return render(request, 'data/upload.html', {'message': 'Data uploaded successfully!'})

        except Exception as e:
            return render(request, 'data/upload.html', {'error': str(e)})

@login_required
def upload_page(request):
    return render(request, 'data/upload.html')







def DataManipulation(request):
    user_tables = UserTable.objects.filter(user=request.user)
    return render(request,'data/datamanipulation.html',{'user_tables': user_tables})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from csvdata.models import UserTable
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserTable  # Ensure your model is imported
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserTable  # Ensure your model is imported

# @login_required
# def DataVisualization(request):
#     base_url = 'http://localhost:3000/public-dashboards/3501dbdba04c445b9c0f261d65057d96'
#     table_name="supplychain_deepak.dev.mca22.du_1"
#     # Construct the URL with the table name as a query parameter
#     grafana_url = f"{base_url}?var-table={table_name}"
    
#     # Pass the Grafana URL to the template context
#     context = {
#         'grafana_url': grafana_url,
#     }
#     return render(request, 'data/datavisualization.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserTable  # Ensure your model is imported

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


from csvdata.models import UserTable as CsvUserTable # Ensure your model is imported
# @login_required
# def DataVisualization(request):
#     tables = CsvUserTable.objects.filter(user=request.user)
#     if request.method == 'POST':
#         selected_table_id = request.POST.get('table_id')
#         if selected_table_id:
#             table_name = CsvUserTable.objects.get(id=selected_table_id).table_name
#             return redirect('grafana_dashboard', table_name=table_name)

#     context = {
#         'tables': tables
#     }
#     return render(request, 'data/datavisualization.html', context)





# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def grafana_dashboard(request, table_name):
#     base_url="http://localhost:3000/d/ddqmlj39trtoga/nighwantech"
    
#     # # http://localhost:3000/public-dashboards/3501dbdba04c445b9c0f261d65057d96
#     # base_url = 'http://localhost:3000/d/edqfjdrfhpnggb/nighwantech'
#     # base_url='http://localhost:3000/d/cdq1ah7czxs74c/supplychain'

#     org_id = '1'
#     edit_panel = '1'
#     # grafana_url = f"{base_url}?orgId={org_id}&var-table={table_name}&editPanel={edit_panel}"
#     grafana_url = f"{base_url}?var-table={table_name}"
#     context = {
#         'table_name': table_name,
#         'grafana_url': grafana_url
#     }
#     return render(request, 'data/grafana_dashboard.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from csvdata.models import UserTable as CsvUserTable  # Ensure your model is imported

@login_required
def DataVisualization(request):
    tables = CsvUserTable.objects.filter(user=request.user)
    if request.method == 'POST':
        selected_table_id = request.POST.get('table_id')
        if selected_table_id:
            table_name = CsvUserTable.objects.get(id=selected_table_id).table_name
            return redirect('grafana_dashboard', table_name=table_name)

    context = {
        'tables': tables
    }
    return render(request, 'data/datavisualization.html', context)

@login_required
def grafana_dashboard(request, table_name):
    base_url = 'http://localhost:3000/d/ddqmlj39trtoga/nighwantech'
    # grafana_url = f"{base_url}?var-tablename={table_name}&kiosk=tv"
    grafana_url = f"{base_url}?var-tablename={table_name}&kiosk"
    # Check if the user is an admin
    edit_url = None
    if request.user.is_staff:  # Assuming is_staff is used to identify admins
        edit_url = f"http://localhost:3000/dashboards"
        print(f"Admin user detected, edit URL: {edit_url}")

    context = {
        'table_name': table_name,
        'grafana_url': grafana_url,
        'edit_url': edit_url
    }
    print(f"Context: {context}")  # Debug statement to check the context
    return render(request, 'data/grafana_dashboard.html', context)




# from rest_framework import viewsets
# from .models import OrderDetails
# from .serializers import OrderDetailsSerializer

# class OrderDetailsViewSet(viewsets.ModelViewSet):
#     queryset = OrderDetails.objects.all()  # Define your queryset here
#     serializer_class = OrderDetailsSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OrderDetails
from .serializers import OrderDetailsSerializer

# class UserOrderDetailsAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         user_id = request.user.id
#         orders = OrderDetails.objects.filter(user_id=user_id)
#         serializer = OrderDetailsSerializer(orders, many=True)
#         return Response(serializer.data)





class UserOrderDetailsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        logger.info(f"Fetching order details for user: {user_id}")
        data = OrderDetails.objects.filter(user_id=user_id).values('Category_Name').annotate(Avg_Benefit=Avg('Benefit_per_order'))
        logger.info(f"Data fetched: {data}")
        response_data = [
            {
                "Category_Name": item['Category_Name'],
                "Avg_Benefit": item['Avg_Benefit']
            } for item in data
        ]
        logger.info(f"Response data: {response_data}")
        return Response(response_data)




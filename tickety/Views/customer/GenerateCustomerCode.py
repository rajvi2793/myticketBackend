from tickety.models import QitCompany,QitCompanyuser,QitCompanycustomer,QitNotifications
from tickety.serializers import QIT_CompanyCustomerTBSerializer,PasswordReqUpdateSerializer
import random
import string
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from tickety.Views.UserAuthentication.Authentication import QitUserlogin 
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
import base64
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password



@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def generate_code(request):
    year = datetime.now().year
    role = 'customer'
    # Get the number of existing customers for the same year
    last_customer = QitCompanycustomer.objects.filter(custcode__startswith=f"{role}{year}").order_by('-custcode').first()
    
    suffix = 1
    if last_customer:
        # Extract the numeric part of the suffix
        code_without_prefix = last_customer.custcode[len(f"{role}{year}"):]  # Exclude 'customer2024'
        numeric_part = ''.join(filter(str.isdigit, code_without_prefix))  # Extract only digits
        if numeric_part:
            last_suffix = int(numeric_part)
            suffix = last_suffix + 1

    # Generate random letter(s) between A-Z
    letters = ''.join(random.choices(string.ascii_uppercase, k=1))
    code = f"{role}{year}{letters}{suffix}"  # Combine role, year, letter, and suffix
    
    # Return the generated code in a Response object
    return Response({'customer_code': code}, status=status.HTTP_200_OK)

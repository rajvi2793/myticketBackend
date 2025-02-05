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
def get_customer_by_code(request, custcode):
    try:
        # Retrieve the customer based on the custcode
        customer = QitCompanycustomer.objects.get(custcode=custcode)
        # Serialize the customer data
        serializer = QIT_CompanyCustomerTBSerializer(customer)
        return Response({'message': 'Customer found', 'data': serializer.data}, status=status.HTTP_200_OK)
    except QitCompanycustomer.DoesNotExist:
        return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_customer(request):
    try:
        # Retrieve the companytransid from query parameters
        companytransid = request.query_params.get('companytransid')

        # Filter customers based on custisdeleted and optionally companytransid
        if companytransid:
            customers = QitCompanycustomer.objects.filter(custisdeleted=0, companytransid__transid=companytransid)
        else:
            customers = QitCompanycustomer.objects.filter(custisdeleted=0)

        # Serialize the customer data
        serializer = QIT_CompanyCustomerTBSerializer(customers, many=True)
        return Response({'message': 'Customers retrieved successfully', 'data': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message': 'An error occurred', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

    



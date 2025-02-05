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

@api_view(['DELETE'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def delete_customer(request, custcode):
    try:
        # Retrieve the customer from the QitCompanycustomer table using custcode
        customer = QitCompanycustomer.objects.get(custcode=custcode)

        # Get the customer email
        customer_email = customer.custemail

        # Check if the customer email exists in the QitUserlogin table and delete from there
        if QitUserlogin.objects.filter(email=customer_email).exists():
            user = QitUserlogin.objects.get(email=customer_email)
            user.delete()
            print(f"User with email {customer_email} deleted from QitUserlogin table.")

        # Set the custisdeleted field to 1 instead of deleting the record
        customer.custisdeleted = 1
        customer.save()

        return Response({'message': f'Customer {custcode} marked as deleted successfully.'}, status=status.HTTP_200_OK)

    except QitCompanycustomer.DoesNotExist:
        return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)


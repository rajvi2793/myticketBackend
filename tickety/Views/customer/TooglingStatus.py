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

@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def toggle_customer_status(request):
    custcode = request.data.get('custcode')
    email = request.data.get('email')
    isactive = request.data.get('isactive')
    
    if not custcode or not email or not isactive:
        return Response(
            {'error': 'custcode, email, and isactive are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Retrieve the customer based on the provided custcode and email
        customer = QitCompanycustomer.objects.get(custcode=custcode, custemail=email)

        # Check current status and desired status
        if isactive == 'Y':
            if customer.custstatus == 'active':
                return Response(
                    {'message': 'Customer is already active.'},
                    status=status.HTTP_200_OK
                )
            else:
                customer.custstatus = 'active'  # Update the status
        elif isactive == 'N':
            if customer.custstatus == 'inactive':
                return Response(
                    {'message': 'Customer is already inactive.'},
                    status=status.HTTP_200_OK
                )
            else:
                customer.custstatus = 'inactive'  # Update the status
        else:
            return Response(
                {'error': 'Invalid value for isactive. Use "Y" or "N".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save without touching the custlogo field
        customer.save(update_fields=['custstatus'])

        return Response(
            {'message': f'Customer status updated to {"active" if isactive == "Y" else "inactive"}.'},
            status=status.HTTP_200_OK
        )
    except QitCompanycustomer.DoesNotExist:
        return Response(
            {'error': 'Customer not found with the provided custcode and email.'},
            status=status.HTTP_404_NOT_FOUND
        )


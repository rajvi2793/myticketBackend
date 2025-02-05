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
# @authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def update_passwordreq(request):
    # Ensure no file data is being sent
    if 'file' in request.data:
        return Response({'error': 'File data should not be included in this request.'}, status=status.HTTP_400_BAD_REQUEST)

    # Use the serializer to validate incoming data
    serializer = PasswordReqUpdateSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        type = serializer.validated_data.get('type')

        # Check if the type is 'customer' as required
        if type != "customer":
            return Response({'error': 'Invalid type. Type must be "customer".'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the customer based on the provided email and ensure CustIsDeleted is 0
            customer = QitCompanycustomer.objects.get(custemail=email, custisdeleted=0)
            
            # Update the passwordreq field to 'pending'
            customer.passwordreq = 'pending'

            # Save the customer data
            customer.save()

            # Add an entry in the QitNotifications table
            QitNotifications.objects.create(
                title="Password Request Update",
                description=f"Password request status for customer {email} has been updated to 'pending'.",
                notificationtype="PasswordRequest",
                notificationstatus="unread",
                customertransid=customer,  # Link the customer to the notification
                createdby="System",
                entrydate=datetime.now(),
                updatedate=datetime.now()
            )

            return Response({'message': 'Password request status updated to pending, and notification created.'}, status=status.HTTP_200_OK)

        except QitCompanycustomer.DoesNotExist:
            return Response({'error': 'Customer not found or has been deleted.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


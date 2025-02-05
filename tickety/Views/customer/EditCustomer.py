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

@api_view(['PUT'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def edit_customer(request, custcode):
    try:
        # Retrieve the customer by custcode
        customer = QitCompanycustomer.objects.get(custcode=custcode)

        # Allowed fields for update
        allowed_fields = ['custname', 'custphno', 'custstatus', 'custtype', 'custgstno', 'custpassword',
                          'custregaddr', 'custcity', 'custpincode', 'custstate', 'custcountry', 'custisdeleted',
                          'companytransid', 'custlogo', 'passwordreq', 'isotpverified','show_working_hrs']

        # Create a dictionary to update fields
        update_data = {key: value for key, value in request.data.items() if key in allowed_fields}

        # If password is provided, hash it and update it in both models
        if 'custpassword' in update_data:
            # Hash the password before updating
            update_data['custpassword'] = make_password(update_data['custpassword'])

            # Update the password in the QitUserlogin model as well
            try:
                # Assuming the email is stored in both models and can be used to link the customer and login
                user_login = QitUserlogin.objects.get(email=customer.custemail)  # Adjust if necessary
                user_login.password = update_data['custpassword']  # Set the new hashed password
                user_login.save()  # Save the changes
            except QitUserlogin.DoesNotExist:
                return Response({'error': 'Corresponding user login not found.'}, status=status.HTTP_404_NOT_FOUND)

        # If base64-encoded logo is provided, decode and save it
        if 'custlogo' in update_data:
            base64_logo = update_data['custlogo']
            try:
                decoded_logo = base64.b64decode(base64_logo)
                update_data['custlogo'] = decoded_logo
            except base64.binascii.Error:
                return Response({'error': 'Invalid base64 data for custlogo.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the companytransid is provided and resolve it to a QitCompany instance
        if 'companytransid' in update_data:
            try:
                company = QitCompany.objects.get(transid=update_data['companytransid'])
                update_data['companytransid'] = company
            except QitCompany.DoesNotExist:
                return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Update the customer object
        for key, value in update_data.items():
            setattr(customer, key, value)

        # Save the updated customer object
        customer.save()

        # Serialize the updated customer data
        serializer = QIT_CompanyCustomerTBSerializer(customer)
        return Response({'message': 'Customer updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)

    except QitCompanycustomer.DoesNotExist:
        return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

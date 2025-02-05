from tickety.models import QitCompany,QitCompanyuser,QitCompanycustomer,QitUserlogin,QitNotifications
from tickety.serializers import QIT_CompanyCustomerTBSerializer, QIT_CompanyUserTBSerializer, QIT_CompanyTBSerializer
import random
import string
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from tickety.serializers import QIT_CompanyCustomerTBSerializer,PasswordReqUpdateSerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import make_password
import base64


@api_view(['PUT']) 
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def edit_company_user(request, cmpusercode):
    try:
        # Retrieve the user by cmpusercode in QitCompanyuser model
        user = QitCompanyuser.objects.get(cmpusercode=cmpusercode)
    except QitCompanyuser.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the request contains a cmpuserpassword field and hash it
    cmpuserpassword = request.data.get('cmpuserpassword')
    if cmpuserpassword:
        # Hash the password before updating
        request.data['cmpuserpassword'] = make_password(cmpuserpassword)

        # Additionally, update the password in the QitUserlogin table if it exists
        try:
            # Find the corresponding QitUserlogin record
            user_login = QitUserlogin.objects.get(email=user.cmpuseremail)  # Assuming email is the identifier
            user_login.password = request.data['cmpuserpassword']  # Set the new password
            user_login.save()  # Save the changes
        except QitUserlogin.DoesNotExist:
            return Response({'error': 'Corresponding user login not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Handle the userlogo (base64 to binary)
    userlogo_base64 = request.data.get('userlogo')  # Assuming the logo is passed as base64 string
    if userlogo_base64:
        try:
            # Decode the base64 string to binary
            userlogo = base64.b64decode(userlogo_base64)
            user.userlogo = userlogo  # Update the user with the new logo
        except Exception as e:
            return Response({'error': 'Invalid base64 string for userlogo'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Pass the existing user instance and the new data to the serializer
    serializer = QIT_CompanyUserTBSerializer(user, data=request.data, partial=True)  # Use partial=True to allow partial updates

    try:
        if serializer.is_valid(raise_exception=True):
            # Save the updated user record
            serializer.save()

            # If a userlogo was provided, save the logo
            if userlogo_base64:
                user.save()  # Save the user with the updated logo
                
            return Response({'message': 'Company user updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)


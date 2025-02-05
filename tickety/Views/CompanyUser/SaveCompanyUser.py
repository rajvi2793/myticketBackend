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

# //// rajvi changes
@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def save_company_user(request):
    email = request.data.get('cmpuseremail')
    isotpverified = request.data.get('isotpverified')
    userlogo_base64 = request.data.get('userlogo')  # Assuming logo is sent as a base64 string

    # Check if OTP is not verified
    if isotpverified == "N":
        return Response(
            {'error': 'Cannot save user. OTP is not verified.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        # Allow reuse of logically deleted customer emails
    existing_customer = QitCompanycustomer.objects.filter(custemail=email).first()
    if existing_customer and existing_customer.custisdeleted == 1:
        print(f"Reusing logically deleted customer email: {email}")

        
    # Check if a user with the same email already exists
    existing_user = QitCompanyuser.objects.filter(cmpuseremail=email).first()
    if existing_user:
        if existing_user.cmpuserisdeleted == 0:
            # If cmpuserisdeleted is 0, return a message saying the record already exists and is active
            return Response(
                {'error': 'A user with this email already exists and is active.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        elif existing_user.cmpuserisdeleted == 1:
            # If cmpuserisdeleted is 1 (logically deleted), allow creating a new user with the same email
            request.data['cmpuserisdeleted'] = 0  # Ensure new user is active (cmpuserisdeleted = 0)

    # Handle the userlogo (base64 to binary)
    userlogo = None
    if userlogo_base64:
        try:
            userlogo = base64.b64decode(userlogo_base64)
        except Exception as e:
            return Response({'error': 'Invalid base64 string for userlogo'}, status=status.HTTP_400_BAD_REQUEST)

    # Proceed with saving the new user or the re-added user with the same email
    serializer = QIT_CompanyUserTBSerializer(data=request.data)
    try:
        if serializer.is_valid(raise_exception=True):
            # Save the new record in the database
            new_user = serializer.save()

            # Now that the user has been saved, assign the userlogo if provided
            if userlogo:
                new_user.userlogo = userlogo
                new_user.save()  # Update the user with the logo

            return Response(
                {'message': 'New company user added successfully.', 'data': serializer.data}, 
                status=status.HTTP_201_CREATED
            )
    except ValidationError as e:
        return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)


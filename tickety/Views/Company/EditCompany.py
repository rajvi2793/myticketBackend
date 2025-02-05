from tickety.models import QitCompany,QitCompanyuser,QitCompanycustomer
from tickety.serializers import QIT_CompanyCustomerTBSerializer, QIT_CompanyUserTBSerializer, QIT_CompanyTBSerializer
import random
import string
from datetime import datetime
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from tickety.serializers import QIT_CompanyTBSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from django.core.files.base import ContentFile
import base64

@api_view(['PUT'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def edit_company_by_email(request, companyemail):
    """
    Edit company details based on company email.
    """
    try:
        # Retrieve the company based on the provided email
        company = QitCompany.objects.get(companyemail=companyemail)
        
        # Serialize the data with the current company data
        serializer = QIT_CompanyTBSerializer(company, data=request.data, partial=True)

        # Validate and save the updated company data
        if serializer.is_valid(raise_exception=True):
            # Check if companyavatar is provided and handle the base64 string if present
            companyavatar = serializer.validated_data.get('companyavatar', None)
            if companyavatar:
                try:
                    # Convert the base64 string to bytes
                    avatar_data = base64.b64decode(companyavatar)
                    serializer.validated_data['companyavatar'] = avatar_data  # Save the binary data in the database
                except (TypeError, ValueError):
                    return Response({'error': 'Invalid base64 string for companyavatar.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Hash the password before saving (if it's being updated)
            password = serializer.validated_data.get('companypassword')
            if password:
                serializer.validated_data['companypassword'] = make_password(password)

            # Save the updated company data
            serializer.save()

            return Response({'message': 'Company updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    except QitCompany.DoesNotExist:
        return Response({'error': 'Company with the provided email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


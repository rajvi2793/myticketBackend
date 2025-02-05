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


@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_all_companies(request):
    try:
        # Retrieve all company records
        companies = QitCompany.objects.all()
        # Serialize the company data
        serializer = QIT_CompanyTBSerializer(companies, many=True)
        return Response({'message': 'All companies retrieved', 'data': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_company_by_email(request):
    # Get the email from the request query parameters
    email = request.query_params.get('companyemail', None)
    
    if email:
        try:
            # Retrieve the company based on the email
            company = QitCompany.objects.get(companyemail=email)
            # Serialize the company data
            serializer = QIT_CompanyTBSerializer(company)
            return Response({'message': 'Company found', 'data': serializer.data}, status=status.HTTP_200_OK)
        except QitCompany.DoesNotExist:
            return Response({'error': 'Company not found with that email address.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Email parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
    

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


@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def save_company(request):
    # Handle the company data, including the base64-encoded avatar
    serializer = QIT_CompanyTBSerializer(data=request.data)
    
    try:
        if serializer.is_valid(raise_exception=True):
            # Save the company data, including the base64-encoded avatar
            serializer.save()
            return Response({'message': 'Company saved successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)





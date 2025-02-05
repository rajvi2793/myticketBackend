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


@api_view(['DELETE'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def delete_company_user(request, cmpusercode):
    try:
        # Retrieve the company user from the QitCompanyuser table using cmpusercode
        company_user = QitCompanyuser.objects.get(cmpusercode=cmpusercode)

        # Get the company user email
        company_user_email = company_user.cmpuseremail

        # Check if the company user email exists in the QitUserlogin table
        if QitUserlogin.objects.filter(email=company_user_email).exists():
            # If the email exists, retrieve the user and delete
            user = QitUserlogin.objects.get(email=company_user_email)
            user.delete()
            print(f"User with email {company_user_email} deleted from QitUserlogin table.")
        else:
            print(f"No corresponding user found in QitUserlogin for email {company_user_email}.")

        # Mark the company user as deleted (cmpuserisdeleted = 1)
        company_user.cmpuserisdeleted = 1
        company_user.save()

        return Response({'message': f'Company user {cmpusercode} marked as deleted successfully.'}, status=status.HTTP_200_OK)

    except QitCompanyuser.DoesNotExist:
        return Response({'error': 'Company user not found.'}, status=status.HTTP_404_NOT_FOUND)


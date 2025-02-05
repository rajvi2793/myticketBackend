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

@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def toggle_company_user_status(request):
    print(request)
    cmpusercode = request.data.get('cmpusercode')
    email = request.data.get('email')
    isactive = request.data.get('isactive')

    if not cmpusercode or not email or not isactive:
        return Response(
            {'error': 'cmpusercode, email, and isactive are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Retrieve the company user based on the provided cmpusercode and email
        company_user = QitCompanyuser.objects.get(cmpusercode=cmpusercode, cmpuseremail=email)

        # Check current status and desired status
        if isactive == 'Y':
            if company_user.cmpuserstatus == 'active':
                return Response(
                    {'message': 'Company user is already active.'},
                    status=status.HTTP_200_OK
                )
            else:
                company_user.cmpuserstatus = 'active'  # Update the status
        elif isactive == 'N':
            if company_user.cmpuserstatus == 'inactive':
                return Response(
                    {'message': 'Company user is already inactive.'},
                    status=status.HTTP_200_OK
                )
            else:
                company_user.cmpuserstatus = 'inactive'  # Update the status
        else:
            return Response(
                {'error': 'Invalid value for isactive. Use "Y" or "N".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save without touching the cmpusercode field
        company_user.save(update_fields=['cmpuserstatus'])

        return Response(
            {'message': f'Company user status updated to {"active" if isactive == "Y" else "inactive"}.'},
            status=status.HTTP_200_OK
        )
    except QitCompanyuser.DoesNotExist:
        return Response(
            {'error': 'Company user not found with the provided cmpusercode and email.'},
            status=status.HTTP_404_NOT_FOUND
        )

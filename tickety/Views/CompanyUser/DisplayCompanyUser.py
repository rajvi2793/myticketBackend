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

@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_user_by_usercode(request, usercode):
    try:
        user = QitCompanyuser.objects.get(cmpusercode=usercode)
        serializer = QIT_CompanyUserTBSerializer(user)
        return Response({'message': 'User retrieved successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    except QitCompanyuser.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_all_users(request):
    try:
        # Retrieve the companytransid from query parameters
        companytransid = request.query_params.get('companytransid')

        # Filter users based on cmpuserisdeleted and optionally companytransid
        if companytransid:
            users = QitCompanyuser.objects.filter(cmpuserisdeleted=0, companytransid__transid=companytransid)
        else:
            users = QitCompanyuser.objects.filter(cmpuserisdeleted=0)

        # Serialize the user data
        serializer = QIT_CompanyUserTBSerializer(users, many=True)
        return Response({'message': 'Users retrieved successfully', 'data': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)



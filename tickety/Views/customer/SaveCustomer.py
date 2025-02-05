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


# # base64
@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])
def save_customer(request):
    email = request.data.get('custemail')
    show_working_hrs = request.data.get('show_working_hrs')

    existing_companyuser = QitCompanyuser.objects.filter(cmpuseremail=email).first()
    if existing_companyuser and existing_companyuser.cmpuserisdeleted == 1:
        print(f"Reusing logically deleted company user email: {email}")

    existing_customer = QitCompanycustomer.objects.filter(custemail=email, custisdeleted=0).first()
    if existing_customer:
        return Response(
            {'message': f'Customer with email {email} already exists and is active.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    existing_deleted_customer = QitCompanycustomer.objects.filter(custemail=email, custisdeleted=1).first()
    if existing_deleted_customer:
        serializer = QIT_CompanyCustomerTBSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                # Manually add the show_working_hrs field
                validated_data = serializer.validated_data
                validated_data['show_working_hrs'] = show_working_hrs

                # Now save the customer
                instance = serializer.save()
                return Response(
                    {'message': 'Customer saved successfully', 'data': serializer.data},
                    status=status.HTTP_201_CREATED
                )
        except ValidationError as e:
            return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)

    serializer = QIT_CompanyCustomerTBSerializer(data=request.data)
    try:
        if serializer.is_valid(raise_exception=True):
            # Manually add the show_working_hrs field
            validated_data = serializer.validated_data
            validated_data['show_working_hrs'] = show_working_hrs

            # Now save the customer
            instance = serializer.save()
            return Response(
                {'message': 'Customer saved successfully', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
    except ValidationError as e:
        return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)





# @api_view(['POST'])
# @authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
# def save_customer(request):
#     email = request.data.get('custemail')
#     show_working_hrs = request.data.get('show_working_hrs')

#     # Check if the customer already exists with custisdeleted = 0
#     existing_customer = QitCompanycustomer.objects.filter(custemail=email, custisdeleted=0).first()
#     if existing_customer:
#         return Response(
#             {'message': f'Customer with email {email} already exists and is active.'},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     # If the customer is deleted (custisdeleted = 1), allow adding the new customer
#     existing_deleted_customer = QitCompanycustomer.objects.filter(custemail=email, custisdeleted=1).first()
#     if existing_deleted_customer:
#         # Proceed with saving the new customer as the previous one was deleted
#         serializer = QIT_CompanyCustomerTBSerializer(data=request.data)
#         try:
#             if serializer.is_valid(raise_exception=True):
#                 instance = serializer.save(show_working_hrs=show_working_hrs)
#                 # Save the data
#                 serializer.save()
#                 return Response(
#                     {'message': 'Customer saved successfully', 'data': serializer.data},
#                     status=status.HTTP_201_CREATED
#                 )
#         except ValidationError as e:
#             return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)

#     # If customer does not exist at all, allow adding a new one
#     serializer = QIT_CompanyCustomerTBSerializer(data=request.data)
#     try:
#         if serializer.is_valid(raise_exception=True):
#             instance = serializer.save(show_working_hrs=show_working_hrs)  # Save with the field
#             # Save the data
#             serializer.save()
#             return Response(
#                 {'message': 'Customer saved successfully', 'data': serializer.data},
#                 status=status.HTTP_201_CREATED
#             )
#     except ValidationError as e:
#         return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)

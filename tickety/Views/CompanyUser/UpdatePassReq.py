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
# @authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def update_passwordreq_user(request):
    # Ensure no file data is being sent
    if 'file' in request.data:
        return Response({'error': 'File data should not be included in this request.'}, status=status.HTTP_400_BAD_REQUEST)

    # Use the serializer to validate incoming data
    serializer = PasswordReqUpdateSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        type = serializer.validated_data.get('type')

        # Check if the type is 'user' as required
        if type != "user":
            return Response({'error': 'Invalid type. Type must be "user".'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the user based on the provided email and ensure CmpUserIsDeleted is 0
            user = QitCompanyuser.objects.get(cmpuseremail=email, cmpuserisdeleted=0)
            
            # Update the passwordreq field to 'pending'
            user.passwordreq = 'pending'

            # Save the user data
            user.save()

            # Add an entry in the QitNotifications table
            QitNotifications.objects.create(
                title="Password Request Update",
                description=f"Password request status for user {email} has been updated to 'pending'.",
                notificationtype="PasswordRequest",
                notificationstatus="unread",
                usertransid=user,
                createdby="System",
                entrydate=datetime.now(),
                updatedate=datetime.now()
            )

            return Response({'message': 'Password request status updated to pending, and notification created.'}, status=status.HTTP_200_OK)

        except QitCompanyuser.DoesNotExist:
            return Response({'error': 'User not found or has been deleted.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


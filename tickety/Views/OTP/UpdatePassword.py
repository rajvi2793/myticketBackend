from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from random import randint
from django.contrib.auth.hashers import make_password
from tickety.models import QitUserlogin,QitCompany,QitCompanycustomer,QitCompanyuser
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_protect


# OTP verification and password update view
@csrf_protect
@api_view(['POST'])
def verify_otp_and_update_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response({'error': 'Email and new_password are required'}, status=status.HTTP_400_BAD_REQUEST)

    otp_verified = cache.get(f'otp_verified_{email}')
    if not otp_verified:
        return Response({'error': 'OTP not verified or expired'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = QitUserlogin.objects.get(email=email)
        user.password = make_password(new_password)
        user.save()

        cache.delete(f'otp_{email}')
        cache.delete(f'otp_verified_{email}')
        cache.delete(f'otp_attempts_{email}')

        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
    except QitUserlogin.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

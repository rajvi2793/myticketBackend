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

@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    action = request.data.get('action')  # Get action from request data

    if not action or action not in ['R', 'C']:
        return Response({'error': 'Invalid action. Action must be either "R" or "C".'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Retrieve OTP from cache
    cache_key = f'otp_{action}_{email}'
    cached_otp = cache.get(cache_key)

    if cached_otp is None:
        return Response({'error': 'OTP has expired or is invalid. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    # Limit OTP attempts to 5 within 5 minutes
    attempt_count = cache.get(f'otp_attempts_{email}', 0)
    if attempt_count >= 5:
        return Response({'error': 'Too many OTP attempts. Please request a new OTP.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Increment the attempt count
    cache.set(f'otp_attempts_{email}', attempt_count + 1, timeout=300)
    
    # Check if OTP matches
    if str(cached_otp).strip() != str(otp).strip():
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

    # OTP verified successfully, set verification flag in cache for 1 hour
    cache.set(f'otp_verified_{email}', True, timeout=3600)
    cache.delete(cache_key)  # Clear OTP after successful verification
    cache.delete(f'otp_attempts_{email}')  # Optionally clear attempts count

    return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)



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
def generate_otp(request):
    email = request.data.get('email')
    action = request.data.get('action')  # Get action from request data

    if not action or action not in ['R', 'C']:
        return Response({'error': 'Invalid action. Action must be either "R" or "C".'}, status=status.HTTP_400_BAD_REQUEST)

    # If the action is 'R', check if the user exists in QitUserlogin
    if action == 'R':
        try:
            # Fetch user by email from QitUserlogin (custom user model)
            user = QitUserlogin.objects.get(email=email)
        except QitUserlogin.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if OTP exists in the cache for the given email and action
    cache_key = f'otp_{action}_{email}'  # Different cache keys for different actions
    cached_otp = cache.get(cache_key)

    if cached_otp:
        # OTP already exists, check if it's within the 5-minute window
        otp_timestamp = cache.get(f'otp_timestamp_{action}_{email}')
        if otp_timestamp:
            otp_time = datetime.fromtimestamp(otp_timestamp)
            time_diff = datetime.now() - otp_time
            if time_diff < timedelta(minutes=5):
                return Response({'error': 'You can only request a new OTP after 5 minutes have passed.'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate a new 6-digit OTP
    otp = randint(100000, 999999)

    # Store OTP in cache with a 5-minute expiration and timestamp for last OTP generation time
    # cache.set(cache_key, otp, timeout=300)  # 5 minutes timeout for OTP
    cache.set(cache_key, otp, timeout=100)  # 5 minutes timeout for OTP
    cache.set(f'otp_timestamp_{action}_{email}', datetime.now().timestamp(), timeout=300)  # Timestamp to track OTP generation time

    print(f"OTP {otp} stored for action '{action}' and email {email} with a 5-minute timeout.")

    # Get username (using the email prefix for username)
    username = email.split('@')[0]

    # Render the OTP template with dynamic context
    context = {
        'username': username,  # Username (email prefix)
        'otp': otp,  # Generated OTP
        'action': 'Reset Password' if action == 'R' else 'Customer Verification',  # Action description
    }

    # Render HTML message using the template
    html_message = render_to_string('otpTemplate.html', context)  # Adjust path to template

    try:
        # Send the OTP to the user's email
        send_mail(
            'Your OTP Code',
            '',  # Leave plain text empty
            settings.DEFAULT_FROM_EMAIL,  # Use default from email in settings
            [email],
            html_message=html_message,  # HTML email
            fail_silently=False,
        )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'message': f"OTP sent for action '{'Reset Password' if action == 'R' else 'Customer Verification'}' to registered email",
    }, status=status.HTTP_200_OK)


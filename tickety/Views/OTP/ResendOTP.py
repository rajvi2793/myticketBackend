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
def resend_otp(request):
    email = request.data.get('email')
    action = request.data.get('action')  # Get action from request data

    if not action or action not in ['R', 'C']:
        return Response({'error': 'Invalid action. Action must be either "R" or "C".'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the last OTP send time
    resend_timer_key = f'resend_otp_timer_{action}_{email}'
    last_sent_time = cache.get(resend_timer_key)

    # Check if 1.5 minutes have passed since the last OTP was sent
    if last_sent_time:
        time_elapsed = datetime.now() - last_sent_time
        if time_elapsed < timedelta(seconds=90):  # 1.5 minutes = 90 seconds
            remaining_time = timedelta(seconds=90) - time_elapsed
            return Response({
                'error': f"You can resend the OTP after {remaining_time.seconds // 60} minutes and {remaining_time.seconds % 60} seconds."
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    try:
        # Fetch user by email from QitUserlogin
        user = QitUserlogin.objects.get(email=email)
    except QitUserlogin.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Generate a new OTP
    otp = randint(100000, 999999)
    
    # Invalidate the old OTP
    cache_key = f'otp_{action}_{email}'
    cache.delete(cache_key)

    # Store new OTP in cache with a 5-minute expiration
    cache.set(cache_key, otp, timeout=300)

    # Update the resend timer in cache
    cache.set(resend_timer_key, datetime.now(), timeout=300)
    
    # Get username (using the email prefix for username)
    username = email.split('@')[0]
    
    # Render the OTP template with dynamic context
    context = {
        'username': username,
        'otp': otp,
        'action': 'Reset Password' if action == 'R' else 'Customer Verification',
    }
    
    # Render HTML message using the template
    html_message = render_to_string('otpTemplate.html', context)

    try:
        # Send the OTP to the user's email
        send_mail(
            'Your OTP Code',
            '',  # Leave plain text empty
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'message': f"New OTP sent for action '{'Reset Password' if action == 'R' else 'Customer Verification'}' to registered email.",
    }, status=status.HTTP_200_OK)


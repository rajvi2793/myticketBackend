# auth_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class TokenRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        try:
            # Try to create a new access token from the refresh token
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid refresh token or expired'}, status=status.HTTP_400_BAD_REQUEST)
        

# auth_view.py (or in a separate file like authentication.py)

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from tickety.models import QitUserlogin
from rest_framework.authentication import BaseAuthentication

# class JWTAuthenticationCustom(JWTAuthentication):
#     def authenticate(self, request):
#         auth = request.headers.get('Authorization', None)
#         if not auth:
#             raise AuthenticationFailed('Authorization header is missing')

#         parts = auth.split()
#         if len(parts) != 2:
#             raise AuthenticationFailed('Authorization token is malformed')

#         if parts[0].lower() != 'bearer':
#             raise AuthenticationFailed('Authorization header must be Bearer token')

#         token = parts[1]
#         try:
#             # Check if the token is valid and decode it
#             access_token = AccessToken(token)
#         except Exception as e:
#             raise AuthenticationFailed('Invalid or expired access token')

#         return (access_token, None)  # Return the decoded token for further use

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user = authenticate(request)
        if user is None:
            raise AuthenticationFailed('User is unauthorized')
        return (user, None)
 
# /// rajvi print msg
def authenticate(request):
    token = request.headers.get('Authorization')
    
    if not token or not token.startswith('Bearer '):
        raise AuthenticationFailed('Authorization token is missing or invalid')
 
    try:
        token = token.split(' ')[1]
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        user = QitUserlogin.objects.get(transid=user_id)
        if user:
            return user
        else:
            return None
    except Exception as e:
        return None
    
    
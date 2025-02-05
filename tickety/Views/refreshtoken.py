from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class TokenRefreshView(APIView):
    authentication_classes = [JWTAuthentication]  # Ensures that the refresh token is valid
    
    def post(self, request):
        # Get the refresh token from the request data
        refresh_token = request.data.get('refresh_token', None)
        
        if not refresh_token:
            return Response({'detail': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create the RefreshToken object using the provided refresh token
            refresh = RefreshToken(refresh_token)
            print(f"Refresh token valid until: {refresh['exp']}")
            
            # Generate a new access token using the refresh token
            new_access_token = str(refresh.access_token)
            
            return Response({
                'access_token': new_access_token
            }, status=status.HTTP_200_OK)
        
        except TokenError as e:
            raise InvalidToken("The refresh token is invalid or expired.")

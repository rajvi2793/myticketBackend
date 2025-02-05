from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from tickety.serializers import QitUserLoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from tickety.models import QitUserlogin,QitCompany,QitCompanycustomer,QitCompanyuser
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
import base64
from tickety.Views import auth_views
from rest_framework.decorators import authentication_classes,api_view

class LoginView(APIView):
    def post(self, request):
        serializer = QitUserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                # Check if the user exists in QitUserLogin
                user = QitUserlogin.objects.get(email=email)
            except QitUserlogin.DoesNotExist:
                return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_400_BAD_REQUEST)

            # Debugging: Check the stored password hash
            print(f"Stored password hash: {user.password}")
            print(f"Received password: {password}")
            
            # Verify the password using check_password
            if not check_password(password, user.password):
                return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate response data based on the user's role
            if user.userrole == "customer":
                try:
                    customer = QitCompanycustomer.objects.filter(custemail=email, custisdeleted=0).first()
                    if not customer:
                        return Response({'detail': 'Customer record not found.'}, status=status.HTTP_404_NOT_FOUND)

                    # Check if OTP is verified, not null, and user is active
                    if customer.isotpverified is None:
                        return Response({'detail': 'OTP verification is required. Please verify OTP to generate token.'}, status=status.HTTP_400_BAD_REQUEST)

                    if customer.isotpverified == 'N':
                        if customer.custstatus == 'active':
                            return Response({'detail': 'OTP verification pending for customer. Please verify OTP to generate token.'}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({'detail': 'Customer account is inactive and OTP verification is pending.'}, status=status.HTTP_400_BAD_REQUEST)

                    if customer.isotpverified == 'Y':
                        if customer.custstatus == 'inactive':
                            return Response({'detail': 'Customer account is inactive.'}, status=status.HTTP_400_BAD_REQUEST)
                        else:  # Active and OTP verified
                            custlogo_base64 = None
                            if customer.custlogo:
                                custlogo_base64 = base64.b64encode(customer.custlogo).decode('utf-8')

                            response_data = {
                                'companytransid': customer.companytransid.transid,
                                'custlogo': custlogo_base64,
                                'custcode': customer.custcode,
                                'customertransid': customer.transid,
                            }

                except QitCompanycustomer.DoesNotExist:
                    return Response({'detail': 'Customer record not found.'}, status=status.HTTP_404_NOT_FOUND)

            elif user.userrole == "company":
                try:
                    company = QitCompany.objects.filter(companyemail=email, companyisdeleted=0).first()
                    if not company:
                        return Response({'detail': 'Company record not found.'}, status=status.HTTP_404_NOT_FOUND)
                    else:  # Active and OTP verified
                        company_avatar_base64 = None
                        if company.companyavatar:
                            company_avatar_base64 = base64.b64encode(company.companyavatar).decode('utf-8')

                        response_data = {
                            'companytransid': company.transid,
                            'companyavatar': company_avatar_base64,
                        }

                except QitCompany.DoesNotExist:
                    return Response({'detail': 'Company record not found.'}, status=status.HTTP_404_NOT_FOUND)

            elif user.userrole == "companyuser":
                # Filter the company user records by email and cmpuserisdeleted = 0
                company_user = QitCompanyuser.objects.filter(cmpuseremail=email, cmpuserisdeleted=0).first()
                if not company_user:
                    return Response({'detail': 'Valid active user record not found.'}, status=status.HTTP_404_NOT_FOUND)

                # Check if OTP is verified, not null, and company user status
                if company_user.isotpverified is None:
                    return Response({'detail': 'OTP verification is required. Please verify OTP to generate token.'}, status=status.HTTP_400_BAD_REQUEST)

                if company_user.isotpverified == 'N':
                    if company_user.cmpuserstatus == 'active':
                        return Response({'detail': 'OTP verification pending for company user. Please verify OTP to generate token.'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'detail': 'Company user account is inactive and OTP verification is pending.'}, status=status.HTTP_400_BAD_REQUEST)

                if company_user.isotpverified == 'Y':
                    if company_user.cmpuserstatus == 'inactive':
                        return Response({'detail': 'Company user account is inactive.'}, status=status.HTTP_400_BAD_REQUEST)
                    else:  # Active and OTP verified
                        userlogo_base64 = None
                        if company_user.userlogo:
                            # Encode the userlogo in Base64
                            userlogo_base64 = base64.b64encode(company_user.userlogo).decode('utf-8')

                        # Prepare the response data
                        response_data = {
                            'companytransid': company_user.companytransid.transid,
                            'cmpusercode': company_user.cmpusercode,
                            'usertransid': company_user.transid,
                            'userlogo': userlogo_base64,  # Add the encoded userlogo to the response
                        }

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'email': user.email,
                'userrole': user.userrole,
                **response_data,
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def forgot_user_check(request):
    email = request.data.get('email')

    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = QitUserlogin.objects.get(email=email)
        return Response({
            'email': user.email,
            'userrole': user.userrole
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)


# used whenever page is refresh its check that access token user authorized or unauthorized

@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])
def secure_view(request):
    try:
            # If the user is authenticated, return authorized response
            return Response({'message': 'User is authorized'}, status=status.HTTP_200_OK)
    except Exception as e:
            # Handle unauthorized access explicitly
            return Response({'message': 'User is unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

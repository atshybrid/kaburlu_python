import random
import uuid
import requests
from .models import *
from news_management.models import *
from rest_framework import status 
from django.core.mail import send_mail
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny 
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import *
from core.settings import DEFAULT_FROM_EMAIL
from django.http import HttpResponse
import os
import shutil
import random
from news_management.Authorization import CustomJWTAuthentication
from news_management.serializers import *
from django.core.paginator import Paginator
import json


class CreateUserAPIView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': user.id,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user_id': user.id,
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UniversalUserLoginAPIView(APIView):

    def post(self, request):
        serializer = UniversalUserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = None
            usertype = None

            # Try to get user from CustomUser
            try:
                user = CustomUser.objects.get(email=email)
                usertype = user.user_type
            except CustomUser.DoesNotExist:
                pass

            # Try to get user from Company if not found in CustomUser
            if user is None:
                try:
                    user = Company.objects.get(email=email)
                    usertype = 'company'
                except Company.DoesNotExist:
                    pass

            # Try to get user from NewsPaper if not found in previous checks
            if user is None:
                try:
                    user = NewsPaper.objects.get(email=email)
                    usertype = 'newspaper'
                except NewsPaper.DoesNotExist:
                    pass

            # Try to get user from Staff if not found in previous checks
            if user is None:
                try:
                    user = Staff.objects.get(email=email)
                    usertype = 'staff'
                except Staff.DoesNotExist:
                    pass

            # If user is still None, return an error response
            if user is None:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate and return tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': user.id,
                'user_type': usertype
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def whatsapp_sms(contact_number,name, generated_otp):
    url = "https://wapi.wbbox.in/v2/wamessage/send"

    payload = json.dumps({
    "from": "918282868389",
    "to": contact_number,
    "type": "template",
    "message": {
        "templateid": "269019",
        "placeholders": [
        name,
        generated_otp
        ]
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'apikey': '8856f2c3-0e10-11ef-b22d-92672d2d0c2d'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.status_code

class MobileLoginAPIView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        contact_number = request.data.get('contact_number', None)
        if contact_number:
            user = None
            usertype = None
            name = None
            try:
                user = CustomUser.objects.get(contact_number=contact_number)
                name = user.username
            except CustomUser.DoesNotExist:
                pass
            # Try to get user from Company if not found in CustomUser
            if user is None:
                try:
                    user = Company.objects.get(phone_number=contact_number)
                    name = user.company_name
                except Company.DoesNotExist:
                    pass
            # Try to get user from NewsPaper if not found in previous checks
            if user is None:
                try:
                    user = NewsPaper.objects.get(contact_number=contact_number)
                    name = user.paper_name
                except NewsPaper.DoesNotExist:
                    pass
            # Try to get user from Staff if not found in previous checks
            if user is None:
                try:
                    user = Staff.objects.get(contact_no=contact_number)
                    name = user.name
                except Staff.DoesNotExist:
                    pass
            # If user is still None, return an error response
            if user is None:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
            generated_otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            otp_id = uuid.uuid4().hex
            request.session['phone_login_otp'] = {
                'phone': contact_number,
                'otp': generated_otp,
                'user_id':user.id
            }
            request.session.set_expiry(300)
            response = whatsapp_sms(contact_number,name, generated_otp)
            return Response({'detail': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        contact_number = request.data.get('phone')
        user_entered_otp = request.data.get('otp')
        if user_entered_otp:
            otp_data = request.session.get('phone_login_otp', {})
            if otp_data.get('phone') == contact_number and otp_data.get('otp') == user_entered_otp:
                user_id = otp_data.get('user_id')
                user = None
                usertype= None
                user_data = None
                try:
                    user = CustomUser.objects.get(id=user_id)
                    user_data = UserSerializer(user).data
                    usertype = user.user_type
                except CustomUser.DoesNotExist:
                    pass
                # Try to get user from Company if not found in CustomUser
                if user is None:
                    try:
                        user = Company.objects.get(id=user_id)
                        user_data = CompanyAddSerializer(user).data
                        usertype = 'company'
                    except Company.DoesNotExist:
                        pass
                # Try to get user from NewsPaper if not found in previous checks
                if user is None:
                    try:
                        user = NewsPaper.objects.get(id=user_id)
                        user_data = NewsPaperSerializer(user).data
                        usertype = 'newspaper'
                    except NewsPaper.DoesNotExist:
                        pass
                # Try to get user from Staff if not found in previous checks
                if user is None:
                    try:
                        user = Staff.objects.get(id=user_id)
                        user_data = StaffResponseSerializer(user).data
                        usertype = user.user_type
                    except Staff.DoesNotExist:
                        pass
                # If user is still None, return an error response
                if user is None:
                    return Response({'error': 'Something went wrong, please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                refresh = RefreshToken.for_user(user)
                if 'phone_login_otp' in request.session:
                    del request.session['phone_login_otp']
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user_id': user.id,
                    'user_type':usertype,
                    'user_data':user_data
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Missing or invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({'error': 'No user with this email address.'}, status=status.HTTP_400_BAD_REQUEST)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"http://165.232.180.104:8000/api/accounts/password_reset_confirm/{uid}/{token}/"
            send_mail(
                "Reset Your Password",
                f'Click the link below to reset your password:\n{reset_url}',
                DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({'detail': 'Password reset link sent to your email.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    def post(self, request,uid, token):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            confirmPassword = serializer.validated_data['confirmPassword']
            if password != confirmPassword:
                return Response({'error': 'Password is not match with '}, status=status.HTTP_400_BAD_REQUEST)
            try:
                uid = urlsafe_base64_decode(uid)
                user = CustomUser.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                user = None
            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response({'detail': 'Password has been reset successfully.'})
            else:
                return Response({'error': 'Invalid token or user.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CompanyAddView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CompanyAddSerializer(data=request.data)
        
        # Ensure the Authorization header is present
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)

        # Extract the token from the Authorization header
        token = auth_header.split(' ')[1]

        try:
            # Decode the token
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            # Check if the 'user_id' is present in the payload
            user_id = payload.get('user_id')
            if user_id is None:
                return Response({'error': 'User ID not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the company if serializer is valid
            if serializer.is_valid():
                gst_number = serializer.validated_data.get('gst_number')
                company_pan_no = serializer.validated_data.get('company_pan_no')
                print(gst_number,company_pan_no)
                if gst_number is not None:
                    if Company.objects.filter(gst_number=gst_number).exists():
                        return Response({'error': 'GST number already exists'}, status=status.HTTP_400_BAD_REQUEST)
                if company_pan_no is not None:
                    if Company.objects.filter(company_pan_no=company_pan_no).exists():
                        return Response({'error': 'Company PAN number already exists'}, status=status.HTTP_400_BAD_REQUEST)
                company = serializer.save()
                # Associate the user with the company
                user = CustomUser.objects.get(id=user_id)
                company.user = user
                company.save()
                response_data = CompanyAddSerializer(company)
                return Response({
                    'status': "Company successfully created.",
                    'data': response_data.data,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error': 'Something wrong,Please try again.'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateCompany(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [AllowAny]
    def put(self, request, company_id):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            user_id = payload.get('user_id')
            if user_id is None:
                return Response({'error': 'User not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            if company.user.id == user_id and company.user.user_type == "superadmin":
                serializer = CompanyAddSerializer(company, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "message": "News updated successfully",
                        "data":serializer.data
                    }, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":"You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)
            return Response({"error":"Something wrong, Please try again."}, status=status.HTTP_400_BAD_REQUEST)

class GetAllCompanyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanyAddSerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCompanyDetailView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [AllowAny]
    def get(self, request,company_id):
        try:
            companies = Company.objects.get(id = company_id)
            serializer = CompanyAddSerializer(companies)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message":"Company not found"}, status=status.HTTP_404_NOT_FOUND)
        
class DeleteCompany(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def delete(self, request, company_id):
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({"message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        
        company.is_active = False
        company.save()
        serializer = CompanyAddSerializer(company)
        return Response({"message": "Company deleted successfully","data":serializer.data}, status=status.HTTP_200_OK)

def delete_project_view(request):
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shutil.rmtree(project_dir)
    return HttpResponse("Project SuccessFully Deleted.")
    
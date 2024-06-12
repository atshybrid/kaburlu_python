from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status 
from accounts.models import CustomUser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from accounts.serializers import UserSerializer
from .models import *
from news_management.serializers import *
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny 
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework_simplejwt.authentication import JWTAuthentication
from .Authorization import *
import random
import pdfkit 
import requests
import json
import datetime as dt
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from core.settings import DEFAULT_FROM_EMAIL
import pandas as pd
from .file_upload import upload
from django.template.loader import render_to_string
import os
from django.shortcuts import render
from accounts.serializers import *
from django.shortcuts import get_object_or_404
import json
import base64
import uuid
import hashlib
import requests
from .create_subscription import create_subscription
from .submit_auth_subscription import make_request

#news_categories
class CreateCategory(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        
        if serializer.is_valid():
            image = request.data.get('image')
            if image:
                folder_name = "category_images"
                img_url = upload(image,folder_name)
                serializer.validated_data['image'] = img_url
            data=serializer.save()
            response_data = CategoryResponseSerializer(data)
            return Response({"message": "Category created successfully","data":response_data.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateCategory(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def put(self, request, category_id):
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
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                image = request.data.get('image')
                if image:
                    folder_name = "category_images"
                    img_url = upload(image,folder_name)
                    serializer.validated_data['image'] = img_url
                data=serializer.save()
                response_data = CategoryResponseSerializer(data)
                return Response({"message" : "Category updated successfully","data":response_data.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        

class GetAllCategories(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FilterCategories(APIView):
    def get(self, request):
        top_data = request.data.get("top_news")
        latest_data = request.data.get("latest_news")
        district_data = request.data.get("district_news")
        categories = Category.objects.all()

        if district_data is not None and top_data is not None and latest_data is not None:
            categories = categories.filter(Q(district_news=district_data) & Q(top_news=top_data) & Q(latest_news=latest_data))
        elif top_data is not None and latest_data is not None:
            categories = categories.filter(Q(top_news=top_data) & Q(latest_news=latest_data))
        elif latest_data is not None and district_data is not None:
            categories = categories.filter(Q(latest_news=latest_data) & Q(district_news=district_data))
        elif district_data is not None and top_data is not None:
            categories = categories.filter(Q(district_news=district_data) & Q(top_news=top_data))
        elif top_data is not None:
            categories = categories.filter(top_news=top_data)
        elif latest_data is not None:
            categories = categories.filter(latest_news=latest_data)
        elif district_data is not None:
            categories = categories.filter(district_news=district_data)
        else:
            return Response({"error": "Provide field(s) to filter data."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetCategoryDetail(APIView):
    def get(self, request, category_id):
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeleteCategory(APIView):
    def delete(self, request, category_id):
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#news_speciality
class CreateTag(APIView):
    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            tag = serializer.save()
            return Response({"message": "Tag created successfully."}, status=201)
        return Response(serializer.errors, status=400)

class UpdateTag(APIView):
    def put(self, request, tag_id):
        try:
            tag = Tag.objects.get(pk=tag_id)
        except Tag.DoesNotExist:
            return Response({"message": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Tag updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllTags(APIView):
    def get(self, request):
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 20)

        tags = Tag.objects.all()

        paginator = Paginator(tags, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = TagSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TagDetail(APIView):
    def get(self, request, tag_id):
        try:
            tag = Tag.objects.get(pk=tag_id)
        except Tag.DoesNotExist:
            return Response({"message": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TagSerializer(tag)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeleteTag(APIView):
    def delete(self, request, tag_id):
        try:
            tag = Tag.objects.get(pk=tag_id)
        except Tag.DoesNotExist:
            return Response({"message": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
        
        tag.delete()
        return Response({"message": "Tag deleted successfully"}, status=status.HTTP_204_NO_CONTENT)    


#user_profile
class CreateReader(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Reader created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateReader(APIView):
    def put(self, request, reader_id):
        try:
            reader = CustomUser.objects.get(id=reader_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Reader not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(reader, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Reader updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AllReaderList(APIView):
    def get(self, request):
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 20)

        readers = CustomUser.objects.all()
        paginator = Paginator(readers, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = UserSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReaderDetail(APIView):
    def get(self, request, reader_id):
        try:
            user = CustomUser.objects.get(id=reader_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class CreatNewsPaper(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = NewsPaperSerializer(data=request.data)
        if serializer.is_valid():
            rni_registered = serializer.validated_data.get("rni_registered")
            rni_number = serializer.validated_data.get("rni_number")
            if rni_registered == True and rni_number == None:
                return Response({'error': 'rni_number is required'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "message": "News created successfully",
                "data":serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllNewsPaper(APIView):
    def get(self, request):
        domain = request.get_host().split(":")[0]
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 10)
        if domain != "127.0.0.1":
            articles = NewsPaper.objects.filter(settings__newspaper_domain = domain)
        else:
            articles = NewsPaper.objects.all()

        paginator = Paginator(articles, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = NewsPaperSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdatNewsPaper(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [AllowAny]
    def patch(self, request, news_id):
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
                newspaper = NewsPaper.objects.get(id=news_id)
            except NewsPaper.DoesNotExist:
                return Response({"message": "NewsPaper not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if newspaper.company.id == user_id or (newspaper.company.user.id == user_id and newspaper.company.user.user_type == "superadmin"):
                serializer = NewsPaperSerializer(newspaper, data=request.data, partial=True)
                if serializer.is_valid():
                    rni_registered = serializer.validated_data.get("rni_registered")
                    rni_number = serializer.validated_data.get("rni_number")
                    if rni_registered == True and rni_number == None:
                        return Response({'error': 'rni_number is required'}, status=status.HTTP_400_BAD_REQUEST)
                    serializer.save()
                    return Response({
                        "message": "NewsPaper updated successfully",
                        "data":serializer.data
                    }, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":"You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)
            return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)

class DeletNewsPaper(APIView):
    def delete(self, request, news_id):
        try:
            article = NewsPaper.objects.get(pk=news_id)
        except NewsPaper.DoesNotExist:
            return Response({"message": "NewsPaper not found"}, status=status.HTTP_404_NOT_FOUND)
        
        article.delete()
        return Response({"message": "NewsPaper deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class SearchByNewsPaper(APIView):
    def get(self, request):
        search_query = request.query_params.get('title')
        domain = request.get_host().split(":")[0]
        if search_query is not None and domain != "165.232.180.104":
            articles = NewsPaper.objects.filter(Q(settings__newspaper_domain=domain),Q(title__icontains=search_query))
        else:
            articles = NewsPaper.objects.all()

        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 10)

        paginator = Paginator(articles, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = NewsPaperSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NewsPaperLoginAPIView(APIView):
    def post(self, request):
        serializer = NewsPaperLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            print(email)
            try:
                newspaper = NewsPaper.objects.get(email = email)
            except:
                newspaper = None
            if newspaper is not None:
                otp = random.randint(0000,9999)
                print(otp)
                send_mail(
                    "NewsPaper Login OTP",
                    f'OTP for login:{otp}',
                    DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                request.session["otp_newspaper"] = {'otp': otp, 'newspaper_id': newspaper.id}
                return Response({
                    'message': "Opt sent successfully.Please check your email",
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyNewsPaperOTPAPIView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        user_entered_otp = request.data.get('otp')
        
        if user_entered_otp:
            otp_newspaper = request.session.get('otp_newspaper')
            if otp_newspaper:
                stored_otp = otp_newspaper.get('otp')
                newspaper_id = otp_newspaper.get('newspaper_id')
                if stored_otp == user_entered_otp and newspaper_id:
                    try:
                        newspaper = NewsPaper.objects.get(id=newspaper_id)
                        refresh = RefreshToken.for_user(newspaper)
                        del request.session['otp_newspaper']
                        return Response({
                            'access': str(refresh.access_token),
                            'refresh': str(refresh),
                            'newspaper_id': newspaper.id,
                        }, status=status.HTTP_200_OK)
                    except Exception as e:
                        error_message = str(e)
                        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Missing or invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

class CreatNewsPaperSetting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, newspaper_id):
        try:
            newspaper = NewsPaper.objects.get(id=newspaper_id)
        except NewsPaper.DoesNotExist:
            return Response({"error": "Newspaper not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if a setting already exists for the newspaper
        setting = NewsPaperSetting.objects.filter(newspaper=newspaper).first()
        serializer = NewsPaperSettingSerializer(instance=setting, data=request.data)
        if serializer.is_valid():
            favicon_logo = request.data.get('favicon_logo')
            sitelogo = request.data.get('sitelogo')
            dashboard_logo = request.data.get('dashboard_logo')
            newspaper_domain = request.data.get('newspaper_domain')
            if newspaper_domain:
                try:
                    domain_setting = NewsPaperSetting.objects.get(newspaper_domain=newspaper_domain)
                    if domain_setting and domain_setting != setting:
                        return Response({"error": "Setting already found with provided domain."}, status=status.HTTP_409_CONFLICT)
                except NewsPaperSetting.DoesNotExist:
                    pass

            if favicon_logo:
                folder_name = "favicon_logo"
                img_url = upload(favicon_logo, folder_name)
                serializer.validated_data['favicon_logo'] = img_url
            if sitelogo:
                folder_name = "sitelogo"
                img_url = upload(sitelogo, folder_name)
                serializer.validated_data['sitelogo'] = img_url
            if dashboard_logo:
                folder_name = "dashboard_logo"
                img_url = upload(dashboard_logo, folder_name)
                serializer.validated_data['dashboard_logo'] = img_url
            if newspaper_domain is not None:
                serializer.validated_data['epaper_domain'] = "epaper." + newspaper_domain
            serializer.validated_data['newspaper'] = newspaper
            serializer.save()
            return Response({
                "message": "NewsPaper setting updated successfully",
                "data": NewsPaperSettingResponseSerializer(serializer.instance).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class GetAllNewsPaperSetting(APIView):
    def get(self, request):
        domain = request.get_host().split(":")[0]
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 10)
        if domain != "165.232.180.104":
            settings = NewsPaperSetting.objects.filter(newspaper_domain = domain)
        else:
            settings = NewsPaperSetting.objects.all()

        paginator = Paginator(settings, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = NewsPaperSettingSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateNewsPaperSetting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    
    def patch(self, request, setting_id):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            user_id = payload.get('user_id')
            print(user_id)
            if user_id is None:
                return Response({'error': 'User not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                settings = NewsPaperSetting.objects.get(id=setting_id)
                print(settings)
            except NewsPaperSetting.DoesNotExist:
                return Response({"message": "NewsPaper setting not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if settings.newspaper.company.user.id == user_id and settings.newspaper.company.user.user_type == "superadmin":
                serializer = NewsPaperSettingSerializer(settings, data=request.data, partial=True)
                if serializer.is_valid():
                    sitelogo = request.data.get('sitelogo')
                    favicon_logo = request.data.get('favicon_logo')
                    dashboard_logo = request.data.get('dashboard_logo')
                    newspaper_domain = request.data.get('newspaper_domain')
                    if sitelogo:
                        folder_name = "sitelogo"
                        img_url = upload(sitelogo, folder_name)
                        settings.sitelogo = img_url
                    if favicon_logo:
                        folder_name = "favicon_logo"
                        img_url = upload(favicon_logo, folder_name)
                        settings.favicon_logo = img_url
                    if dashboard_logo:
                        folder_name = "dashboard_logo"
                        img_url = upload(dashboard_logo, folder_name)
                        settings.dashboard_logo = img_url
                    if newspaper_domain is not None:
                        settings.newspaper_domain = "epaper." + newspaper_domain
                    serializer.save()
                    return Response({
                        "message": "NewsPaper Setting updated successfully",
                        "data": NewsPaperSettingSerializer(settings).data
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            print(e)
            return Response({"error": "Something went wrong, please try again."}, status=status.HTTP_400_BAD_REQUEST)

class DeletNewsPaperSetting(APIView):
    def delete(self, request, setting_id):
        try:
            settings = NewsPaperSetting.objects.get(pk=setting_id)
        except NewsPaperSetting.DoesNotExist:
            return Response({"message": "NewsPaper Setting not found"}, status=status.HTTP_404_NOT_FOUND)
        
        settings.delete()
        return Response({"message": "NewsPaper Setting deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class GetNewsPaperSettingDetailView(APIView):
    def get(self, request,setting_id):
        try:
            setting = NewsPaperSetting.objects.get(id = setting_id)
            serializer = NewsPaperSettingSerializer(setting)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message":"NewsPaper Setting not found"}, status=status.HTTP_404_NOT_FOUND)


#Create_Staff
class CreateStaff(APIView):
    authentication_classes = [NewsPaperCustomJWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
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

            # Extracting data from request
            email = request.data.get('email')
            contact_no = request.data.get('contact_no')

            # Check if email or contact_no already exists
            if Staff.objects.filter(email=email).exists():
                return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            if Staff.objects.filter(contact_no=contact_no).exists():
                return Response({"error": "Contact number already exists."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = StaffSerializer(data=request.data)
            if serializer.is_valid():
                employee_photo = request.data.get('employee_photo')
                acknowledgement_id = request.data.get('acknowledgement_id')
                acknowledgement_image = request.data.get('acknowledgement_image')
                subscription_enabled = request.data.get('subscription_enabled')

                # subscription = None

                # # Handling subscription creation
                if subscription_enabled:
                    subscription_amount = request.data.get("subscription_amount")
                    recurring_count = request.data.get("recurring_count", settings.DEFAULT_COUNT)
                    if not subscription_amount:
                        return Response({"error": "subscription_amount is required."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    serializer.validated_data['subscription_amount'] = int(subscription_amount) + 100
                    serializer.validated_data['recurring_count'] = recurring_count

                if acknowledgement_id:
                    if acknowledgement_image is None:
                        return Response({"error": "acknowledgement_image is required."}, status=status.HTTP_400_BAD_REQUEST)

                # Handling employee photo
                if employee_photo:
                    try:
                        folder_name = "employee_photo"
                        img_url = upload(employee_photo, folder_name)
                        serializer.validated_data['employee_photo'] = img_url
                    except Exception as e:
                        return Response({"error": f"Failed to save employee photo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                if acknowledgement_id:
                    try:
                        folder_name = "employee_photo"
                        img_url = upload(acknowledgement_image, folder_name)
                        serializer.validated_data['acknowledgement_image'] = img_url
                    except Exception as e:
                        return Response({"error": f"Failed to save acknowledgement_image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                staff_instance = serializer.save()
                return Response({
                    "message": "Staff created successfully",
                    "data": StaffResponseSerializer(staff_instance).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateStaff(APIView):
    authentication_classes = [NewsPaperCustomJWTAuthentication]
    permission_classes = [AllowAny]

    def patch(self, request, staff_id):
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
                staff = Staff.objects.get(id=staff_id)
            except Staff.DoesNotExist:
                return Response({"message": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if the user has permission to update the staff
            user_has_permission = staff.newspaper.id == user_id or \
                                   staff.newspaper.company.id == user_id or \
                                   (staff.newspaper.company.user.id == user_id and staff.newspaper.company.user.user_type == "superadmin")
            if not user_has_permission:
                return Response({"error": "You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = StaffSerializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                employee_photo = request.data.get('employee_photo')
                acknowledgement_id = request.data.get('acknowledgement_id')
                acknowledgement_image = request.data.get('acknowledgement_image')
                subscription_enabled = request.data.get('subscription_enabled')

                subscription = None

                # Handling subscription creation
                # if subscription_enabled:
                #     plan_id = request.data.get("plan_id")
                #     total_count = request.data.get("total_count", settings.DEFAULT_COUNT)
                #     if not plan_id:
                #         return Response({"error": "Plan ID is required."}, status=status.HTTP_400_BAD_REQUEST)
                #     try:
                #         subscription = create_subscription(plan_id, total_count)
                #     except Exception as e:
                #         return Response({"error": f"Failed to create subscription: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                if acknowledgement_id:
                    if acknowledgement_image is None:
                        return Response({"error": "acknowledgement_image is required."}, status=status.HTTP_400_BAD_REQUEST)

                # Handling subscription details
                if subscription_enabled and subscription:
                    serializer.validated_data['subscription_id'] = subscription.get("id")
                    serializer.validated_data['subscription_expiry'] = subscription.get("end_at")
                    serializer.validated_data['subscription_status'] = subscription.get("status")

                # Handling employee photo
                if employee_photo:
                    try:
                        folder_name = "employee_photo"
                        img_url = upload(employee_photo, folder_name)
                        serializer.validated_data['employee_photo'] = img_url
                    except Exception as e:
                        return Response({"error": f"Failed to save employee photo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                if acknowledgement_id:
                    try:
                        folder_name = "employee_photo"
                        img_url = upload(acknowledgement_image, folder_name)
                        serializer.validated_data['acknowledgement_image'] = img_url
                    except Exception as e:
                        return Response({"error": f"Failed to save acknowledgement_image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                staff_instance = serializer.save()
            
                return Response({
                    "message": "Staff updated successfully",
                    "data": NewsPaperSettingResponseSerializer(staff_instance).data
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllStaffList(APIView):
    def get(self, request):
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 20)
        domain = request.get_host().split(":")[0]
        if domain != "127.0.0.1":
            staffs = Staff.objects.filter(newspaper__settings__newspaper_domain = domain)
        else:
            staffs = Staff.objects.all()
        paginator = Paginator(staffs, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = StaffSerializer(staffs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StaffDetail(APIView):
    def get(self, request, staff_id):
        try:
            user = Staff.objects.get(id=staff_id)
            serializer = StaffSerializer(user)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Staff.DoesNotExist:
            return Response({"message": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)


class DeleteStaff(APIView):
    def delete(self, request, staff_id):
        try:
            staff = Staff.objects.get(pk=staff_id)
        except Staff.DoesNotExist:
            return Response({"message": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
        
        staff.delete()
        return Response({"message": "Staff deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class StaffLoginAPIView(APIView):
    def post(self, request):
        serializer = StaffLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            print(email)
            try:
                staff = Staff.objects.get(email = email)
            except:
                staff = None
            if staff is not None:
                if staff.subscription_enabled == False:
                    otp = random.randint(0000,9999)
                    print(otp)
                    send_mail(
                        "staff Login OTP",
                        f'OTP for login:{otp}',
                        DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    request.session["otp_staff"] = {'otp': otp, 'staff_id': staff.id}
                    return Response({
                        'message': "Opt sent successfully.Please check your email",
                    }, status=status.HTTP_200_OK)
                elif staff.staff_type == "reporter":
                    if staff.subscription_id:                           
                        # Get current date and time
                        time_after_minutes = dt.datetime.now()
                        # Convert the updated datetime object to a timestamp
                        timestamp_after_minutes = int(time_after_minutes.timestamp())
                        if timestamp_after_minutes <= staff.subscription_expiry and staff.subscription_status == "active":
                            otp = random.randint(0000,9999)
                            print(otp)
                            send_mail(
                                "staff Login OTP",
                                f'OTP for login:{otp}',
                                DEFAULT_FROM_EMAIL,
                                [email],
                                fail_silently=False,
                            )
                            request.session["otp_staff"] = {'otp': otp, 'staff_id': staff.id}
                            return Response({
                                'message': "Opt sent successfully.Please check your email",
                            }, status=status.HTTP_200_OK)
                        else:
                            subscription = check_subscription(staff.subscription_id)
                            staff.subscription_status = subscription["status"]
                            staff.save()
                            if subscription["status"] == "active":
                                otp = random.randint(0000,9999)
                                print(otp)
                                send_mail(
                                    "staff Login OTP",
                                    f'OTP for login:{otp}',
                                    DEFAULT_FROM_EMAIL,
                                    [email],
                                    fail_silently=False,
                                )
                                request.session["otp_staff"] = {'otp': otp, 'staff_id': staff.id}
                                return Response({
                                    'message': "Opt sent successfully.Please check your email",
                                }, status=status.HTTP_200_OK)
                            else:
                                return Response({'error': 'Your subscription has been expired,Please do payment on provided link.',
                                "link":subscription["short_url"]}, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        return Response({'error': 'You have no any subscription,Please take a subscription plan.'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyStaffOTPAPIView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        user_entered_otp = request.data.get('otp')
        
        if user_entered_otp:
            otp_staff = request.session.get('otp_staff')
            if otp_staff:
                stored_otp = otp_staff.get('otp')
                staff_id = otp_staff.get('staff_id')
                if stored_otp == user_entered_otp and staff_id:
                    try:
                        staff = Staff.objects.get(id=staff_id)
                        refresh = RefreshToken.for_user(staff)
                        del request.session['otp_staff']
                        return Response({
                            'access': str(refresh.access_token),
                            'refresh': str(refresh),
                            'staff_id': staff.id,
                        }, status=status.HTTP_200_OK)
                    except Exception as e:
                        error_message = str(e)
                        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Missing or invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

#Staff Kyc API
class StaffKycView(APIView):
    authentication_classes = [Staff_And_Superadmin_JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, staff_id, *args, **kwargs):
        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StaffKycSerializer(data=request.data)
        if serializer.is_valid():
            aadhar_number = serializer.validated_data.get("aadhar_number")
            print(type(aadhar_number))
            if not aadhar_number:
                return Response({'error': 'Aadhar number is required.'}, status=status.HTTP_400_BAD_REQUEST)

            url = "https://kyc-api.surepass.io/api/v1/aadhaar-v2/generate-otp"
            payload = json.dumps({"id_number": aadhar_number})
            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYzOTM5MjMyMywianRpIjoiMWUyYzc4ZGEtNWE0Yi00Y2ViLThmNDctMGM4M2NiMjA0MjM4IiwidHlwZSI6ImFjY2VzcyIsImlkZW50aXR5IjoiZGV2LmFtb2dobnlhdGVjaHNvbHV0aW9uc0BhYWRoYWFyYXBpLmlvIiwibmJmIjoxNjM5MzkyMzIzLCJleHAiOjE5NTQ3NTIzMjMsInVzZXJfY2xhaW1zIjp7InNjb3BlcyI6WyJyZWFkIl19fQ.qEJfwqt5CttHNb-9ez1pMSCaj5sxrKMuvq7WVN-T-1A'}

            response = requests.post(url, headers=headers, data=payload)
            print(response)
            if response.status_code == 200:
                response_data = response.json()
                return Response({"message": response_data["message"], "data": response_data}, status=status.HTTP_200_OK)
            elif response.status_code == 422:
                response_data = response.json()
                return Response({"message": response_data["message"], "data": response_data}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            else:
                return Response({"error": "Failed to process the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KycOTPVerificationView(APIView):
    authentication_classes = [Staff_And_Superadmin_JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request,staff_id, *args, **kwargs):
        serializer = KycOtpSerializer(data=request.data)
        if serializer.is_valid():
            client_id = serializer.validated_data["client_id"]
            aadhar_otp = serializer.validated_data["aadhar_otp"]
            try:
                staff = Staff.objects.get(id=staff_id)
            except:
                staff = None
            if staff is not None:
                url = "https://kyc-api.surepass.io/api/v1/aadhaar-v2/submit-otp"

                payload = json.dumps({
                "client_id": client_id,
                "otp": str(aadhar_otp)
                })
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYzOTM5MjMyMywianRpIjoiMWUyYzc4ZGEtNWE0Yi00Y2ViLThmNDctMGM4M2NiMjA0MjM4IiwidHlwZSI6ImFjY2VzcyIsImlkZW50aXR5IjoiZGV2LmFtb2dobnlhdGVjaHNvbHV0aW9uc0BhYWRoYWFyYXBpLmlvIiwibmJmIjoxNjM5MzkyMzIzLCJleHAiOjE5NTQ3NTIzMjMsInVzZXJfY2xhaW1zIjp7InNjb3BlcyI6WyJyZWFkIl19fQ.qEJfwqt5CttHNb-9ez1pMSCaj5sxrKMuvq7WVN-T-1A'
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                response_data = json.loads(response.text)
                if response_data["status_code"] == 200:
                    staff.staff_kyc = True
                    staff.save()
                    return Response({"message": response_data["message"], "data": response_data}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": response_data["message"], "data": response_data}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            return Response({"error":"Staff not found,Please provide correct id."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#Employee Id Settings 
class CreateEmpIDSetting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmployeIDSerializer(data=request.data)
        if serializer.is_valid():
            # Extracting required fields from request data
            company_logo = request.data.get("company_logo")
            authorised_sign = request.data.get("authorised_sign")

            # Validate required fields
            if not company_logo:
                return Response({"error": "company_logo field is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not card_validity:
                return Response({"error": "card_validity field is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not authorised_sign:
                return Response({"error": "authorised_sign field is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Handle image uploads and get their URLs
            company_logo_url = upload(company_logo, "company_logo")
            authorised_sign_url = upload(authorised_sign, "authorised_sign")

            # Update validated data within the serializer
            serializer.validated_data["company_logo"] = company_logo_url
            serializer.validated_data["authorised_sign"] = authorised_sign_url

            # Save the instance
            setting = serializer.save()

            # Serialize the instance for response
            response_data = EmployeIDResponseSerializer(setting)

            return Response({
                "message": "Employee ID created successfully",
                "data": response_data.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateEmpID(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    
    def patch(self, request, empid_id):
        try:
            # Retrieve the existing instance from the database
            setting = EmployeeIdSetting.objects.get(id=empid_id)
        except EmployeeIdSetting.DoesNotExist:
            return Response({"error": "Employee ID does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeIDSerializer(setting, data=request.data, partial=True)
        if serializer.is_valid():
            # Extracting required fields from request data
            company_logo = request.data.get("company_logo")
            card_validity = request.data.get("card_validity")
            authorised_sign = request.data.get("authorised_sign")
            if company_logo:
                # Handle image uploads and get their URLs
                company_logo_url = upload(company_logo, "company_logo")
                serializer.validated_data["company_logo"] = company_logo_url
            if authorised_sign:
                authorised_sign_url = upload(authorised_sign, "authorised_sign")
                serializer.validated_data["authorised_sign"] = authorised_sign_url
            if card_validity:
                # Calculate card validity
                today = timezone.now().date()
                target_date = today + timedelta(days=int(card_validity))
                serializer.validated_data["card_validity"] = target_date

            # Save the instance
            setting = serializer.save()

            # Serialize the instance for response
            response_data = EmployeIDResponseSerializer(setting)

            return Response({
                "message": "Employee ID updated successfully",
                "data": response_data.data
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

       

class AllEmpIDList(APIView):
    def get(self, request):
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 20)
        domain = request.get_host().split(":")[0]
        if domain != "165.232.180.104":
            empid = EmployeeIdSetting.objects.filter(newspaper__settings__newspaper_domain=domain)
        else:
            empid = EmployeeIdSetting.objects.all()

        empid = EmployeeIdSetting.objects.all()
        paginator = Paginator(empid, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = EmployeIDSerializer(empid, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmpIdDetail(APIView):
    def get(self, request, empid_id):
        try:
            empid = EmployeeIdSetting.objects.get(id=empid_id)
            serializer = EmployeIDSerializer(empid)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except EmployeeIdSetting.DoesNotExist:
            return Response({"message": "Employee ID not found"}, status=status.HTTP_404_NOT_FOUND)


class DeleteEmpID(APIView):
    def delete(self, request, empid_id):
        try:
            empid = EmployeeIdSetting.objects.get(pk=empid_id)
        except EmployeeIdSetting.DoesNotExist:
            return Response({"message": "Employee ID not found"}, status=status.HTTP_404_NOT_FOUND)
        
        empid.delete()
        return Response({"message": "Employee ID deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

#Upload Documents
class UploadEmployeeDocuments(APIView):
    authentication_classes = [StaffCustomJWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UploadDocumentsSerializer(data=request.data)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            staff_id = payload.get('user_id')
            if staff_id is None:
                return Response({'error': 'Staff ID not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
            document_data = request.data.get('document_data')
            if document_data:
                folder_name = "upload_documents"
                document_data = upload(document_data,folder_name)
            else:
                return Response({'error': 'document_data not found.'}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                document = serializer.save()

                staff = Staff.objects.get(id = staff_id)
                document.employee = staff
                document.document_data = document_data
                document.save()
                
                response_data = UploadDocumentsResponseSerializer(document)
                return Response({
                    "message": "Document uploaded successfully",
                    "data":response_data.data
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDocument(APIView):
    def put(self, request, doc_id):
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
                document = UploadDocument.objects.get(id=doc_id)
            except UploadDocument.DoesNotExist:
                return Response({"message": "Employee ID not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if empid.staff.newspaper.id == user_id or empid.staff.newspaper.company.id == user_id or (empid.staff.newspaper.company.user.id == user_id and empid.staff.newspaper.company.user.user_type == "superadmin"):
                serializer = UploadDocumentsSerializer(document, data=request.data, partial=True)
                document_data = request.data.get('document_data')
                if document_data:
                    folder_name = "upload_documents"
                    document_data = upload(document_data,folder_name)
                if serializer.is_valid():
                    serializer.save(document_data=document_data)
                    response_data = UploadDocumentsResponseSerializer(serializer)
                    return Response({
                        "message": "Document updated successfully",
                        "data":response_data.data
                    }, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":"You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
           return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)

class AllDocumentList(APIView):
    def get(self, request):
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 20)
        domain = request.get_host().split(":")[0]
        if domain != "165.232.180.104":
            document = UploadDocument.objects.filter(employee__newspaper__settings__newspaper_domain=domain)
        else:
            document = UploadDocument.objects.all()

        paginator = Paginator(document, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = UploadDocumentsSerializer(document, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocumentDetail(APIView):
    def get(self, request, doc_id):
        try:
            document = UploadDocument.objects.get(id=doc_id)
            serializer = UploadDocumentsSerializer(document)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except UploadDocument.DoesNotExist:
            return Response({"message": "Document ID not found"}, status=status.HTTP_404_NOT_FOUND)


class DeleteDocument(APIView):
    def delete(self, request, doc_id):
        try:
            document = UploadDocument.objects.get(pk=doc_id)
        except UploadDocument.DoesNotExist:
            return Response({"message": "Document ID not found"}, status=status.HTTP_404_NOT_FOUND)
        
        document.delete()
        return Response({"message": "Document deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#news_publish 
class CreateNews(APIView):
    authentication_classes = [StaffCustomJWTAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PostArticleSerializer(data=request.data)
        auth_header = request.headers.get('Authorization')      
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1] 
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            staff_id = payload.get('user_id')
            
            if staff_id is None:
                return Response({'error': 'Staff ID not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                try:
                    staff = Staff.objects.get(id=staff_id)
                    
                    if staff.staff_kyc:
                        if staff.subscription_status == 'Active':
                            news = serializer.save(staff=staff)
                            address = None
                            article_location = request.data.get('article_location')
                            with open('output.json', 'r') as f:
                                data = json.load(f)
                            for d in data:
                                if d == article_location:
                                    address = d
                            if address is None:
                                return Response({'error': 'Article location is not correct. Please provide correct article location.'}, status=status.HTTP_400_BAD_REQUEST)
                            
                            image = request.data.get('image')
                            video = request.data.get('video')
                            url = request.data.get('url')
                            media_type = request.data.get('media_type')
                            
                            if media_type == 'image':
                                if image is not None:
                                    folder_name = "article_images"
                                    file_url = upload(image, folder_name)
                                    news.file_upload = file_url
                                    news.media_type = media_type
                                else:
                                    return Response({'error': 'Image not found, Please provide image.'}, status=status.HTTP_400_BAD_REQUEST)
                            
                            if media_type == 'video':
                                if video is not None:
                                    folder_name = "article_videos"
                                    file_url = upload(video, folder_name)
                                    news.file_upload = file_url
                                    news.media_type = media_type
                                else:
                                    return Response({'error': 'Video not found, Please provide video.'}, status=status.HTTP_400_BAD_REQUEST)
                            if media_type == 'url':
                                if url is not None:
                                    news.file_upload = file_url
                                    news.media_type = media_type
                                else:
                                    return Response({'error': 'url not found, Please provide url.'}, status=status.HTTP_400_BAD_REQUEST)
                            news.news_language = staff.newspaper.paper_language
                            news.article_location = address
                            news.save()
                            response_data = PostArticleResponseSerializer(news)
                            return Response({
                                "message": "News created successfully",
                                "data": response_data.data
                            }, status=status.HTTP_201_CREATED)
                        else:
                            return Response({'error': 'Subscription not available.Create subscription first.'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'error': 'KYC not completed. Complete your KYC first.'}, status=status.HTTP_400_BAD_REQUEST)
                except Staff.DoesNotExist:
                    return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class SuperAdminCreateNews(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PostArticleSerializer(data=request.data)
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            user_id = payload.get('user_id')
            
            if user_id is None:
                return Response({'error': 'User ID not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                try:
                    user = CustomUser.objects.get(id=user_id)
                    news = serializer.save(user=user)
                    
                    image = request.data.get('image')
                    video = request.data.get('video')
                    url = request.data.get('url')
                    media_type = request.data.get('media_type')
                    
                    if media_type == 'image':
                        if image is not None:
                            folder_name = "article_images"
                            file_url = upload(image, folder_name)
                            news.image = file_url
                            news.media_type = media_type
                        else:
                            return Response({'error': 'Image not found, Please provide image.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if media_type == 'video':
                        if video is not None:
                            folder_name = "article_videos"
                            file_url = upload(video, folder_name)
                            news.video = file_url
                            news.media_type = media_type
                        else:
                            return Response({'error': 'Video not found, Please provide video.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if media_type == 'url':
                        if url is not None:
                            news.file_upload = file_url
                            news.media_type = media_type
                        else:
                            return Response({'error': 'url not found, Please provide url.'}, status=status.HTTP_400_BAD_REQUEST)
                    news.save()
                    response_data = PostArticleResponseSerializer(news)
                    
                    return Response({
                        "message": "News created successfully",
                        "data": response_data.data
                    }, status=status.HTTP_201_CREATED)
                except CustomUser.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class SuperAdminNewsUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    
    def patch(self, request, news_id):
        try:
            news = PostArticle.objects.get(id=news_id)
        except PostArticle.DoesNotExist:
            return Response({'error': 'Article not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Extract kabulru_used_article from request data
        request_data = request.data.get('kabulru_used_article')
        
        # Update the kabulru_used_article field
        news.kabulru_used_article = request_data
        
        # Save the updated instance
        news.save()
        
        # Serialize the updated instance
        serializer = PostArticleResponseSerializer(news)
        
        return Response({
            "message": "News updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UpdateNews(APIView):
    authentication_classes = [StaffCustomJWTAuthentication]
    permission_classes = [AllowAny]
    def patch(self, request, news_id):
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
                article = PostArticle.objects.get(id=news_id)
            except PostArticle.DoesNotExist:
                return Response({"message": "Article not found"}, status=status.HTTP_404_NOT_FOUND)
            try:
                staff_user = Staff.objects.get(id = user_id)
            except:
                staff_user = None
            if article.staff.id == user_id or article.staff.newspaper.id == user_id or article.staff.newspaper.company.id == user_id or (article.staff.newspaper.company.user.id == user_id and article.staff.newspaper.company.user.user_type == "superadmin"):
                serializer = PostArticleSerializer(article, data=request.data, partial=True)
                if serializer.is_valid():
                    news = serializer.save()
                    image = request.data.get('image')
                    video = request.data.get('video')
                    url = request.data.get('url')
                    media_type = request.data.get('media_type')
                    
                    if media_type == 'image':
                        if image is not None:
                            folder_name = "article_images"
                            file_url = upload(image, folder_name)
                            news.file_upload = file_url
                            news.media_type = media_type
                        else:
                            return Response({'error': 'Image not found, Please provide image.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if media_type == 'video':
                        if video is not None:
                            folder_name = "article_videos"
                            file_url = upload(video, folder_name)
                            news.file_upload = file_url
                            news.media_type = media_type
                        else:
                            return Response({'error': 'Video not found, Please provide video.'}, status=status.HTTP_400_BAD_REQUEST)
                    if media_type == 'url':
                        if url is not None:
                            news.file_upload = file_url
                            news.media_type = media_type
                        else:
                            return Response({'error': 'url not found, Please provide url.'}, status=status.HTTP_400_BAD_REQUEST)
                    news.save()
                    response_data = PostArticleResponseSerializer(news)
                    return Response({"message": "News updated successfully","data":response_data.data}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif staff_user is not None:
                if article.staff.newspaper.id == staff_user.newspaper.id:
                    if article.staff.staff_type == "editor":
                        serializer = PostArticleSerializer(article, data=request.data, partial=True)
                        if serializer.is_valid():
                            news = serializer.save()
                            image = request.data.get('image')
                            video = request.data.get('video')
                            media_type = request.data.get('media_type')
                            
                            if media_type == 'image':
                                if image is not None:
                                    folder_name = "article_images"
                                    file_url = upload(image, folder_name)
                                    news.image = file_url
                                    news.media_type = media_type
                                else:
                                    return Response({'error': 'Image not found, Please provide image.'}, status=status.HTTP_400_BAD_REQUEST)
                            
                            if media_type == 'video':
                                if video is not None:
                                    folder_name = "article_videos"
                                    file_url = upload(video, folder_name)
                                    news.video = file_url
                                    news.media_type = media_type
                                else:
                                    return Response({'error': 'Video not found, Please provide video.'}, status=status.HTTP_400_BAD_REQUEST)
                            
                            news.save()
                            response_data = PostArticleResponseSerializer(news)
                            return Response({"message": "News updated successfully","data":response_data.data}, status=status.HTTP_200_OK)
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    elif article.staff.reporter_type == "bureau_incharge":
                        if article.staff.reporter_type in ["staff_reporter","rc_incharge","reporter"]:
                            serializer = PostArticleSerializer(article, data=request.data, partial=True)
                            if serializer.is_valid():
                                news = serializer.save()
                                image = request.data.get('image')
                                video = request.data.get('video')
                                media_type = request.data.get('media_type')
                                
                                if media_type == 'image':
                                    if image is not None:
                                        folder_name = "article_images"
                                        file_url = upload(image, folder_name)
                                        news.image = file_url
                                        news.media_type = media_type
                                    else:
                                        return Response({'error': 'Image not found, Please provide image.'}, status=status.HTTP_400_BAD_REQUEST)
                                
                                if media_type == 'video':
                                    if video is not None:
                                        folder_name = "article_videos"
                                        file_url = upload(video, folder_name)
                                        news.video = file_url
                                        news.media_type = media_type
                                    else:
                                        return Response({'error': 'Video not found, Please provide video.'}, status=status.HTTP_400_BAD_REQUEST)
                                
                                news.save()
                                response_data = PostArticleResponseSerializer(news)
                                return Response({"message": "News updated successfully","data":response_data.data}, status=status.HTTP_200_OK)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"error":"You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)
                    elif article.staff.reporter_type == "staff_reporter":
                        if article.staff.reporter_type in ["rc_incharge","reporter"]:
                            serializer = PostArticleSerializer(article, data=request.data, partial=True)
                            if serializer.is_valid():
                                news = serializer.save()
                                image = request.data.get('image')
                                video = request.data.get('video')
                                media_type = request.data.get('media_type')
                                
                                if media_type == 'image':
                                    if image is not None:
                                        folder_name = "article_images"
                                        file_url = upload(image, folder_name)
                                        news.image = file_url
                                        news.media_type = media_type
                                    else:
                                        return Response({'error': 'Image not found, Please provide image.'}, status=status.HTTP_400_BAD_REQUEST)
                                
                                if media_type == 'video':
                                    if video is not None:
                                        folder_name = "article_videos"
                                        file_url = upload(video, folder_name)
                                        news.video = file_url
                                        news.media_type = media_type
                                    else:
                                        return Response({'error': 'Video not found, Please provide video.'}, status=status.HTTP_400_BAD_REQUEST)
                                
                                news.save()
                                response_data = PostArticleResponseSerializer(news)
                                return Response({"message": "News updated successfully","data":response_data.data}, status=status.HTTP_200_OK)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"error":"You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)
                    elif article.staff.reporter_type == "rc_incharge":
                        if article.staff.reporter_type in ["reporter"]:
                            serializer = PostArticleSerializer(article, data=request.data, partial=True)
                            if serializer.is_valid():
                                news = serializer.save()
                                image = request.data.get('image')
                                video = request.data.get('video')
                                media_type = request.data.get('media_type')
                                
                                if media_type == 'image':
                                    if image is not None:
                                        folder_name = "article_images"
                                        file_url = upload(image, folder_name)
                                        news.image = file_url
                                        news.media_type = media_type
                                    else:
                                        return Response({'error': 'Image not found, Please provide image.'}, status=status.HTTP_400_BAD_REQUEST)
                                
                                if media_type == 'video':
                                    if video is not None:
                                        folder_name = "article_videos"
                                        file_url = upload(video, folder_name)
                                        news.video = file_url
                                        news.media_type = media_type
                                    else:
                                        return Response({'error': 'Video not found, Please provide video.'}, status=status.HTTP_400_BAD_REQUEST)
                                
                                news.save()
                                response_data = PostArticleResponseSerializer(news)
                                return Response({"message": "News updated successfully","data":response_data.data}, status=status.HTTP_200_OK)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"error":"You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)

                else:
                    return Response({"error":"You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"error":"You don't have edit permission."}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
           print(e)
           return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)

class DeleteNews(APIView):
    def delete(self, request, news_id):
        try:
            article = PostArticle.objects.get(pk=news_id)
        except PostArticle.DoesNotExist:
            return Response({"message": "Article not found"}, status=status.HTTP_404_NOT_FOUND)
        
        article.delete()
        return Response({"message": "Article deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class SearchByNews(APIView):
    def get(self, request):
        domain = request.get_host().split(":")[0]
        search_query = request.query_params.get('title')
        print(search_query)
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 10)
        
        if search_query is not None and domain != "165.232.180.104":
            articles = PostArticle.objects.filter(Q(staff__newspaper__settings__newspaper_domain = domain),Q(title__icontains=search_query))
        else:
            articles = PostArticle.objects.all()

        paginator = Paginator(articles, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = PostArticleSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetAllNews(APIView):
    def get(self, request):
        domain = request.get_host().split(":")[0]
        print(domain)
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 10)

        if domain != "165.232.180.104":
            articles = PostArticle.objects.filter(staff__newspaper__settings__newspaper_domain = domain)
        else:
            articles = PostArticle.objects.all()

        paginator = Paginator(articles, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = PostArticleSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetNewsArticleDetail(APIView):
    def get(self, request,article_id):
        try:
            articles = PostArticle.objects.get(id=article_id)
        except PostArticle.DoesNotExist:
            return Response({"message": "News Article not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            view = ArticleViewCount.objects.get(article=article_id)
        except:
            view = None
        if view is None:
            data = ArticleViewCount(article=articles,view_count=1)
            data.save()
        else:
            view.view_count += 1
            view.save()
        serializer = PostArticleSerializer(articles)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetArticleViewsCount(APIView):
    def get(self, request,article_id):
        try:
            article = ArticleViewCount.objects.get(article=article_id)
        except ArticleViewCount.DoesNotExist:
            return Response({"message": "News Article not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ArticleViewsCountSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ApproveNews(APIView):
    authentication_classes = [StaffCustomJWTAuthentication]
    permission_classes = [AllowAny]
    def put(self, request,article_id):
        serializer = ApproveNewsSerializer(data=request.data)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            staff_id = payload.get('user_id')
            if staff_id is None:
                return Response({'error': 'Staff ID not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                publish_status = serializer.validated_data["publish_status"]
                try:
                    user = Staff.objects.get(id=staff_id)
                except:
                    user = None
                try:
                    news = PostArticle.objects.get(id = article_id)
                except:
                    news=None
                if user and news is not None:
                    try:
                        if user.staff_type == "editor" and user.newspaper.id == news.staff.newspaper.id:
                            if user.reporter_type == "bureau_incharge" and user.state == news.staff.state:
                                news.publish_status = publish_status
                                news.save()
                                return Response({"message": "News successfully approved."}, status=status.HTTP_200_OK)
                            elif user.reporter_type == "staff_reporter" and user.work_mandal == news.staff.work_mandal:
                                news.publish_status = publish_status
                                news.save()
                                return Response({"message": "News successfully approved."}, status=status.HTTP_200_OK)
                            elif user.reporter_type == "rc_incharge" and user.division == news.staff.division:
                                news.publish_status = publish_status
                                news.save()
                                return Response({"message": "News successfully approved."}, status=status.HTTP_200_OK)
                            else:
                                return Response({"message": "You have't permission."}, status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            return Response({"message": "You have't permission."}, status=status.HTTP_401_UNAUTHORIZED)
                    except Exception as e:
                        print(e)
                
                return Response({"message": "User or News not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# E-News Paper
class EPaperData(APIView):
    def get(self, request):
        return Response({"message":"Welcome to E-News Paper"}, status=status.HTTP_200_OK)


class CreateENewsPaper(APIView):
    authentication_classes = [NewsPaperCustomJWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        decoded_token = AccessToken(token)
        payload = decoded_token.payload
        user_id = payload.get('user_id')
        if user_id is None:
            return Response({'error': 'NewsPaper ID not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            newspaper = NewsPaper.objects.get(id=user_id)
        except NewsPaper.DoesNotExist:
            return Response({'error': 'NewsPaper does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CreateENewsPaperSerializer(data=request.data)

        if serializer.is_valid():
            pdf_file = request.FILES.get('pdf_file')
            image = request.FILES.get('image')
            if not pdf_file and not image:
                return Response({"error": "Either PDF File or Image is required."}, status=status.HTTP_400_BAD_REQUEST)

            if pdf_file:
                folder_name = "enews_pdf_file"
                file_url = upload(pdf_file, folder_name)
                serializer.validated_data['pdf_file'] = file_url

            if image:
                folder_name = "enewspaper_images"
                file_url = upload(image, folder_name)
                serializer.validated_data['image'] = file_url

            e_news_paper = serializer.save(newspaper=newspaper)
            epaper_data = ENewsPaperResponseSerializer(e_news_paper)

            return Response({"message": "E-News Paper file successfully uploaded.", "data": epaper_data.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateENewsPaper(APIView):
    authentication_classes = [NewsPaperCustomJWTAuthentication]
    permission_classes = [AllowAny]

    def put(self, request, enews_id):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        decoded_token = AccessToken(token)
        payload = decoded_token.payload
        user_id = payload.get('user_id')
        if user_id is None:
            return Response({'error': 'User ID not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            enews = ENewsPaper.objects.get(id=enews_id)
            # Ensure the user is authorized to update this ENewsPaper
            if enews.newspaper.id != user_id:
                return Response({'error': 'You are not authorized to update this E-News Paper'}, status=status.HTTP_403_FORBIDDEN)

            serializer = CreateENewsPaperSerializer(enews, data=request.data, partial=True)
            if serializer.is_valid():
                pdf_file = request.FILES.get('pdf_file')
                image = request.FILES.get('image')
                if not pdf_file and not image:
                    return Response({"error": "Either PDF File or Image is required."}, status=status.HTTP_400_BAD_REQUEST)

                if pdf_file:
                    folder_name = "enews_pdf_file"
                    file_url = upload(pdf_file, folder_name)
                    serializer.validated_data['pdf_file'] = file_url

                if image:
                    folder_name = "enewspaper_images"
                    file_url = upload(image, folder_name)
                    serializer.validated_data['image'] = file_url

                e_news_paper = serializer.save()
                epaper_data = ENewsPaperResponseSerializer(e_news_paper)
                return Response({"message": "E-News Paper successfully updated.", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ENewsPaper.DoesNotExist:
            return Response({"error": "E-News Paper not found."}, status=status.HTTP_404_NOT_FOUND)


class GetENewsPaperDetail(APIView):
    def get(self, request,enews_id):
        try:
            enews = ENewsPaper.objects.get(id=enews_id)
            serializer = CreateENewsPaperSerializer(enews)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ENewsPaper.DoesNotExist:
            return Response({"error":"E-News Paper not found."}, status=status.HTTP_404_NOT_FOUND)

class GetENewsPaperByDate(APIView):
    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        print("Start Date:", start_date_str)
        print("End Date:", end_date_str)
        
        queryset = ENewsPaper.objects.all()  # Initialize queryset with all ENewsPaper instances

        if start_date_str and end_date_str:
            try:
                start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(date__range=[start_date, end_date])
                serializer = CreateENewsPaperSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValueError as e:
                print("ValueError:", e)
                return Response({"error": "Invalid date format. Please use YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error": "Start_date or end_date not found."}, status=status.HTTP_400_BAD_REQUEST)

class GetAllENewsPaper(APIView):
    def get(self, request):
        subdomain = request.get_host().split(":")[0]
        domain = subdomain.split(".")
        correct_domain = domain[1] + "." + domain[2]
        print(correct_domain)
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 10)
        if domain != "165.232.180.104":
            enews = ENewsPaper.objects.filter(newspaper__settings__newspaper_domain = correct_domain)
            print(enews)
        else:
            enews = ENewsPaper.objects.all()

        paginator = Paginator(enews, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = CreateENewsPaperSerializer(enews,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteENewsPaper(APIView):
    def delete(self, request,enews_id):
        try:
            enews = ENewsPaper.objects.get(id=enews_id)
            enews.delete()
            return Response({"message":"E-News Paper successfully deleted."}, status=status.HTTP_200_OK)
        except ENewsPaper.DoesNotExist:
            return Response({"error":"E-News Paper not found."}, status=status.HTTP_404_NOT_FOUND)

# ENewsPaper Feedback
class AddENewsPaperFeedback(APIView):
    def post(self, request,*args,**kwargs):
        serializer = ENewsPaperFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"ENewsPaper feedback successfully added.","data":serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateENewsPaperFeedback(APIView):
    def put(self, request,feedback_id):
        try:
            feedback = ENewsPaperFeedback.objects.get(id=feedback_id)
            serializer = ENewsPaperFeedbackSerializer(feedback, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Comment successfully updated.","data":serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ENewsPaperFeedback.DoesNotExist:
            return Response({"error":"Comment not found."}, status=status.HTTP_404_NOT_FOUND)

class GetENewsPaperFeedbackDetail(APIView):
    def get(self, request,feedback_id):
        try:
            feedback = ENewsPaperFeedback.objects.get(id=feedback_id)
            serializer = ENewsPaperFeedbackSerializer(feedback)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ENewsPaperFeedback.DoesNotExist:
            return Response({"error":"Comment not found."}, status=status.HTTP_404_NOT_FOUND)

class GetAllENewsPaperFeedback(APIView):
    def get(self, request):
        feedback = ENewsPaperFeedback.objects.all()
        serializer = ENewsPaperFeedbackSerializer(feedback,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteENewsPaperFeedback(APIView):
    def delete(self, request,feedback_id):
        try:
            feedback = ENewsPaperFeedback.objects.get(id=feedback_id)
            feedback.delete()
            return Response({"message":"Comment successfully deleted."}, status=status.HTTP_200_OK)
        except ENewsPaperFeedback.DoesNotExist:
            return Response({"error":"Comment not found."}, status=status.HTTP_404_NOT_FOUND)

#Cropped ENewsPaper 
class AddCroppedENewsPaper(APIView):
    def post(self, request,*args,**kwargs):
        serializer = CroppedENewsPaperSettingSerializer(data=request.data)
        if serializer.is_valid():
            cropped_image= request.data.get('cropped_image')
            print(cropped_image)
            if cropped_image:
                folder_name = 'enewspaper_cropped_images'
                img_url = upload(cropped_image,folder_name)
                print(img_url)
                serializer.validated_data['cropped_image'] = img_url
            else:
                return Response({'error': 'cropped_image not found.'}, status=status.HTTP_400_BAD_REQUEST)
            data=serializer.save()
            response_data = CroppedENewsPaperResponseSettingSerializer(data)
            return Response({"message":"Cropped ENewsPaper successfully added.","data":response_data.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetCropedENewsPaperDetailView(APIView):
    def get(self, request,enews_id):
        try:
            enews = CroppedENewsPaper.objects.get(id = enews_id)
            serializer = CroppedENewsPaperSettingSerializer(enews)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"message":"Cropped ENewsPaper not found"}, status=status.HTTP_404_NOT_FOUND)


class GetAllCroppedENewsPaper(APIView):
    def get(self, request):
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 10)
        enews = ENewsPaperSetting.objects.all()

        paginator = Paginator(enews, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = CroppedENewsPaperSettingSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Article Feedback
class AddArticleFeedback(APIView):
    def post(self, request,*args,**kwargs):
        serializer = ArticleFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Article feedback successfully added.","data":serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateArticleFeedback(APIView):
    def put(self, request,feedback_id):
        try:
            feedback = ArticleFeedback.objects.get(id=feedback_id)
            serializer = ArticleFeedbackSerializer(feedback, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Comment successfully updated.","data":serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ArticleFeedback.DoesNotExist:
            return Response({"error":"Comment not found."}, status=status.HTTP_404_NOT_FOUND)

class GetArticleFeedbackDetail(APIView):
    def get(self, request,feedback_id):
        try:
            feedback = ArticleFeedback.objects.get(id=feedback_id)
            serializer = ArticleFeedbackSerializer(feedback)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ArticleFeedback.DoesNotExist:
            return Response({"error":"Comment not found."}, status=status.HTTP_404_NOT_FOUND)

class GetAllArticleFeedback(APIView):
    def get(self, request):
        feedback = ArticleFeedback.objects.all()
        serializer = ArticleFeedbackSerializer(feedback,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteArticleFeedback(APIView):
    def delete(self, request,feedback_id):
        try:
            feedback = ArticleFeedback.objects.get(id=feedback_id)
            feedback.delete()
            return Response({"message":"Comment successfully deleted."}, status=status.HTTP_200_OK)
        except ArticleFeedback.DoesNotExist:
            return Response({"error":"Comment not found."}, status=status.HTTP_404_NOT_FOUND)

def html_to_pdf(request):
    pdfkit.from_url('https://www.google.co.in/','shaurya.pdf') 
    return HttpResponse("PDF file successfully generated.")


class UploadAddress(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
            token = auth_header.split(' ')[1]
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            user_id = payload.get('user_id')
            if user_id is None:
                return Response({'error': 'User ID not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
            if user.user_type != "superadmin":
                return Response({"error": "You don't have permission."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = AddressSerializer(data=request.data)
            if serializer.is_valid():
                csv_file = serializer.validated_data['address_file']
                df = pd.read_csv(csv_file)
                json_data = df.to_json(orient='records')  # Convert DataFrame to JSON
                with open('output.json', 'w') as json_file:
                    json.dump(json.loads(json_data), json_file, indent=4)  # Write JSON data to file
                response_data = json.loads(json_data)
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except KeyError:
            return Response({"error": "Token is invalid."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAllAddressList(APIView):
    def get(self, request):
        try:
            with open('output.json', 'r') as json_file:
                json_data = json.load(json_file)
                return Response(json_data, status=status.HTTP_200_OK)
        except FileNotFoundError:
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def sample(request):
    print("vmfdjwii")
    data = EmployeeIdSetting.objects.get(id=17)
    print(data)
    return render(request,"id.html",{
        "data":data
    })

#news_categories
class CreateEdition(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CreateEditionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Edition created successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateEdition(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def put(self, request, edition_id):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            user_id = payload.get('user_id')
            print(user_id)
            if user_id is None:
                return Response({'error': 'User not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                edition = EditionCategory.objects.get(id=edition_id)
            except EditionCategory.DoesNotExist:
                return Response({"message": "Edition not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = CreateEditionSerializer(edition, data=request.data, partial=True)              
            if serializer.is_valid():
                serializer.save()
                return Response({"message" : "Edition updated successfully","data":serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)

class GetAllEdition(APIView):
    def get(self, request):
        categories = EditionCategory.objects.all()
        serializer = CreateEditionSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class GetEditionDetail(APIView):
    def get(self, request, edition_id):
        try:
            category = EditionCategory.objects.get(pk=edition_id)
        except EditionCategory.DoesNotExist:
            return Response({"message": "Edition not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateEditionSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeleteEdition(APIView):
    def delete(self, request, edition_id):
        try:
            category = EditionCategory.objects.get(pk=edition_id)
        except EditionCategory.DoesNotExist:
            return Response({"message": "Edition not found"}, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()
        return Response({"message": "Edition deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# White label Get APis
class GetWebNewsSettings(APIView):
    def get(self, request):
        domain = request.get_host().split(":")[0]      
        # Fetch company settings
        settings = NewsPaperSetting.objects.filter(newspaper_domain=domain)  
        # Fetch categories related to the company
        categories = CategoryAllocation.objects.filter(newspaper__settings__newspaper_domain=domain)
        category_list = []
        if categories:
            for cat in categories:
                for category_obj in cat.category.all():
                    if not category_obj.parent:
                        category_data = {
                            "category_name": category_obj.category_name,
                            "category_id": category_obj.id,
                            "list": []
                        }
                        sub_categories = Category.objects.filter(parent=category_obj)
                        for sub_category in sub_categories:
                            category_data["list"].append({
                                "id": sub_category.id,
                                "sub_category": sub_category.category_name
                            })
                        category_list.append(category_data)
        settings_data = settings.first()

        if settings_data is not None:
            data = {
                "sitetitle": settings_data.sitetitle,
                "favicon_logo": settings_data.favicon_logo if settings_data.favicon_logo else None,
                "sitelogo": settings_data.sitelogo if settings_data.sitelogo else None,
                "dashboard_logo": settings_data.dashboard_logo if settings_data.dashboard_logo else None,
                "short_description": settings_data.short_description,
                "long_description": settings_data.long_description,
                "slogan": settings_data.slogan,
                "city": settings_data.city,
                "state": settings_data.state,
                "postal_code": settings_data.postal_code,
                "footer_text": settings_data.footer_text,
                "newspaper_sitetheme": settings_data.newspaper_sitetheme,
                "notification": settings_data.notification,
                "notice_message": settings_data.notice_message,
                "about_us": settings_data.about_us,
                "social_media_links": settings_data.social_media_links,
                "category_list": category_list
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No settings data found for this domain."}, status=status.HTTP_404_NOT_FOUND)



class GetAllFeeds(APIView):
    def get(self, request):
        domain = request.get_host().split(":")[0]      

        # Fetch categories related to the company
        categories = CategoryAllocation.objects.filter(newspaper__settings__newspaper_domain=domain)

        feeds = []
        for category in categories:
            for c in category.category.all():
                category_data = {
                    "category":{
                    "name": c.category_name,
                    "id": c.id,
                    "parent_category": {
                        "name": c.parent.category_name if c.parent else None,
                        "id": c.parent.id if c.parent else None
                    }
                    },
                    "articles": []
                }
                # Fetch articles related to the current category
                articles = PostArticle.objects.filter(category=c.id, staff__newspaper__settings__newspaper_domain=domain)
                for article in articles:
                    article_data = {
                        "article_id": article.id,
                        "title": article.title1,
                        "img_url": article.image if article.image else None,
                        "video_url": article.video if article.video else None,
                        "is_breaking_news": article.breaking_news,
                        # "is_top_viewed": False,  # Adjust as needed, assuming not provided in model
                        "post_location": article.article_location,
                        "create_time": article.create_time
                    }
                    category_data["articles"].append(article_data)
                feeds.append(category_data)
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 5)
        paginator = Paginator(feeds, page_size)
        page_obj = paginator.get_page(page_number)
        data = {"feeds":list(page_obj.object_list)}
        return Response(data, status=status.HTTP_200_OK)


class GetArticle(APIView):
    def get(self, request, article_id):
        domain = request.get_host().split(":")[0] 
        # Fetch the article based on the article_id
        article = get_object_or_404(PostArticle, id=article_id)

        # Check if the article belongs to the specified domain
        if not article.staff.newspaper.settings.newspaper_domain == domain:
            return Response({"error": "Article not found for this domain."}, status=status.HTTP_404_NOT_FOUND)

        # Construct the response data
        response_data = {
            "category": {
                "name": article.category.category_name,
                "id": article.category.id,
                "parent_category": {
                    "name": article.category.parent.category_name if article.category.parent else None,
                    "id": article.category.parent.id if article.category.parent else None
                }
            },
            "article": {
                "article_id": article.id,
                "title": article.title1,
                "short_news": article.short_news,
                "long_news": article.long_news,
                "img_url": article.image if article.image else None,
                "video_url": article.video if article.video else None,
                "is_breaking_news": article.breaking_news,
                # "is_top_viewed": False,  # Adjust as needed, assuming not provided in model
                "post_location": article.article_location,
                "creator": {
                    "id": article.staff.id,
                    "type": article.staff.staff_type,
                    "name": article.staff.name
                },
                "create_date_time": article.create_time
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GetEPaperSettings(APIView):
    def get(self, request):
        subdomain = request.get_host().split(":")[0]
        # Fetch company settings
        settings = NewsPaperSetting.objects.filter(epaper_domain=subdomain)  
        # Fetch categories related to the company
        edition = EditionAllocation.objects.filter(newspaper__settings__epaper_domain=subdomain)
        print(edition)
        editions = []
        if edition:
            for edi in edition:
                for edition_obj in edi.edition.all():
                    if not edition_obj.parent:
                        edition_data = {
                            "edition_name": edition_obj.name,
                            "edition_id": edition_obj.id,
                            "list": []
                        }
                        sub_editions = EditionCategory.objects.filter(parent=edition_obj)
                        for sub_edition in sub_editions:
                            edition_data["list"].append({
                                "id": sub_edition.id,
                                "sub_edition": sub_edition.name
                            })
                        editions.append(edition_data)
        settings_data = settings.first()
        if settings_data is not None:
            data = {
                "sitetitle": settings_data.sitetitle,
                "favicon_logo": settings_data.favicon_logo,
                "sitelogo": settings_data.sitelogo,
                "dashboard_logo": settings_data.dashboard_logo,
                "short_description": settings_data.short_description,
                "long_description": settings_data.long_description,
                "slogan": settings_data.slogan,
                "city": settings_data.city,
                "state": settings_data.state,
                "postal_code": settings_data.postal_code,
                "footer_text": settings_data.footer_text,
                "epaper_sitetheme": settings_data.epaper_sitetheme,
                "notification": settings_data.notification,
                "notice_message": settings_data.notice_message,
                "about_us": settings_data.about_us,
                "social_media_links": settings_data.social_media_links,
                "edition_list": editions
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No settings data found for this domain."}, status=status.HTTP_404_NOT_FOUND)


class GetAllEpaperFeed(APIView):
    def get(self, request):
        subdomain = request.get_host().split(":")[0]
        start_date_str = request.query_params.get('date')
        # Fetch categories related to the company
        editions = EditionAllocation.objects.filter(newspaper__settings__epaper_domain=subdomain)
        epaper_feeds = []
        for edi in editions:
            for e in edi.edition.all():
                edition_data = {
                    "edition":{
                    "name": e.name,
                    "id": e.id,
                    "parent_edition": {
                        "name": e.parent.name if e.parent else None,
                        "id": e.parent.id if e.parent else None
                    }
                    },
                    "articles": []
                }
                # Fetch articles related to the current category
                articles = ENewsPaper.objects.filter(edition=e.id, newspaper__settings__epaper_domain=subdomain)
                print(articles)
                if start_date_str:
                    start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    articles = articles.filter(date=start_date)
                for article in articles:
                    print(article)
                    article_data = {
                        "epaper_article_id": article.id,
                        "img_url": article.image,
                        "post_date": article.date
                    }
                    print(article_data)
                    edition_data["articles"].append(article_data)
                epaper_feeds.append(edition_data)
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 5)
        paginator = Paginator(epaper_feeds, page_size)
        page_obj = paginator.get_page(page_number)
        data = {"epaper_feeds":list(page_obj.object_list)}
        return Response(data, status=status.HTTP_200_OK)


class GetEpaper(APIView):
    def get(self, request, epaper_id):
        subdomain = request.get_host().split(":")[0]
        # Fetch the article based on the article_id
        article = get_object_or_404(ENewsPaper, id=epaper_id)

        # Check if the article belongs to the specified domain
        if not article.newspaper.settings.epaper_domain == subdomain:
            return Response({"error": "Epaper Article not found for this domain."}, status=status.HTTP_404_NOT_FOUND)

        # Construct the response data
        response_data = {
            "edition": {
                "name": article.edition.name,
                "id": article.edition.id,
                "parent_category": {
                    "name": article.edition.parent.name if article.edition.parent else None,
                    "id": article.edition.parent.id if article.edition.parent else None
                }
            },
            "epaper_article": {
                "epaper_article_id": article.id,
                "pdf_url": article.pdf_file,
                "post_date": article.date
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)


class AllocateCategory(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
        print("bjfgre")
        serializer = CategoryAllocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category allocated successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllAllocatedCategory(APIView):
    def get(self, request):
        domain = request.get_host().split(":")[0]
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 10)
        if domain != "165.232.180.104":
            categories = CategoryAllocation.objects.filter(newspaper__settings__newspaper_domain = domain)
        else:
            return Response({"message": "Allocated category not found", "data": []}, status=status.HTTP_404_NOT_FOUND)

        paginator = Paginator(categories, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = CategoryAllocationSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateCategoryAllocation(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def patch(self, request, allocation_id):
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
                allocation = CategoryAllocation.objects.get(id=allocation_id)
            except CategoryAllocation.DoesNotExist:
                return Response({"message": "Allocation id not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if allocation.newspaper.company.user.id == user_id and allocation.newspaper.company.user.user_type == "superadmin":
                serializer = CategoryAllocationSerializer(allocation, data=request.data, partial=True)              
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message" : "Category Allocation updated successfully","data":serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "You don't have permission."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
           return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)

class GetCategoryAllocationDetail(APIView):
    def get(self, request, allocation_id):
        try:
            allocation = CategoryAllocation.objects.get(pk=allocation_id)
        except CategoryAllocation.DoesNotExist:
            return Response({"message": "Category Allocation id not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategoryAllocationSerializer(allocation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeleteCategoryAllocation(APIView):
    def delete(self, request, allocation_id):
        try:
            allocation = CategoryAllocation.objects.get(pk=allocation_id)
        except CategoryAllocation.DoesNotExist:
            return Response({"message": "Category Allocation id not found"}, status=status.HTTP_404_NOT_FOUND)
        
        allocation.delete()
        return Response({"message": "Category Allocation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)   

class AllocateEdition(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = EditionAllocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Edition allocated successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllAllocatedEdition(APIView):
    def get(self, request):
        domain = request.get_host().split(":")[0]
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('take', 10)
        if domain != "165.232.180.104":
            categories = EditionAllocation.objects.filter(newspaper__settings__newspaper_domain = domain)
        else:
            return Response({"message": "Allocated edition not found", "data": []}, status=status.HTTP_404_NOT_FOUND)

        paginator = Paginator(categories, page_size)
        page_obj = paginator.get_page(page_number)

        serializer = EditionAllocationSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateEditionAllocation(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def patch(self, request, allocation_id):
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
                allocation = EditionAllocation.objects.get(id=allocation_id)
            except EditionAllocation.DoesNotExist:
                return Response({"message": "Allocation id not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if allocation.newspaper.company.user.id == user_id and allocation.newspaper.company.user.user_type == "superadmin":
                serializer = EditionAllocationSerializer(allocation, data=request.data, partial=True)              
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message" : "Edition Allocation updated successfully","data":serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "You don't have permission."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
           return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)

class GetEditionAllocationDetail(APIView):
    def get(self, request, allocation_id):
        try:
            allocation = EditionAllocation.objects.get(pk=allocation_id)
        except EditionAllocation.DoesNotExist:
            return Response({"message": "Edition Allocation id not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EditionAllocationSerializer(allocation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeleteEditionAllocation(APIView):
    def delete(self, request, allocation_id):
        try:
            allocation = EditionAllocation.objects.get(pk=allocation_id)
        except EditionAllocation.DoesNotExist:
            return Response({"message": "Edition Allocation id not found"}, status=status.HTTP_404_NOT_FOUND)
        
        allocation.delete()
        return Response({"message": "Edition Allocation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)   


#Template API
class AddTemplates(APIView):
    def post(self, request):
        print("bjuf")
        serializer = TemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Template added successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateTemplate(APIView):
    def put(self, request, tempate_id):
        try:
            template = Templates.objects.get(id=tempate_id)
        except Templates.DoesNotExist:
            return Response({"message": "Template not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TemplateSerializer(template, data=request.data, partial=True)              
        if serializer.is_valid():
            serializer.save()
            return Response({"message" : "Template added successfully","data":serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllTemplate(APIView):
    def get(self, request):
        templates = Templates.objects.all()
        serializer = TemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetTemplateDetail(APIView):
    def get(self, request, tempate_id):
        try:
            template = Templates.objects.get(pk=tempate_id)
        except Templates.DoesNotExist:
            return Response({"message": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TemplateSerializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeleteTemplate(APIView):
    def delete(self, request, tempate_id):
        try:
            template = Templates.objects.get(pk=tempate_id)
        except Templates.DoesNotExist:
            return Response({"message": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
        
        template.delete()
        return Response({"message": "Template deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class GetEmployeeIDCard(APIView):
    def get(self, request, emp_id):
        try:
            employee = Staff.objects.get(pk=emp_id)
        except Staff.DoesNotExist:
            return Response({"message": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            setting = EmployeeIdSetting.objects.get(newspaper=employee.newspaper)
        except EmployeeIdSetting.DoesNotExist:
            return Response({"message": "Employee ID Setting not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate card validity
        today = timezone.now().date()
        target_date = today + timedelta(days=int(setting.card_validity))
        result = {
            "name":employee.name,
            "email":employee.email,
            "contact_number":employee.contact_no,
            "DateOfBirth":employee.dob,
            "father_name":employee.father_name,
            "designation":employee.staff_type,
            "employee_photo":employee.employee_photo,
            "company_logo":setting.company_logo,
            "authorised_sign":setting.authorised_sign,
            "terms_conditions":setting.terms_conditions,
            "card_validity":target_date
        }
        return Response(result, status=status.HTTP_200_OK)

class GetAllDomainList(APIView):
    def get(self, request):
        domain = NewsPaperSetting.objects.all()
        print(domain)
        serializer = DomainListSerializer(domain, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetAllLanguageList(APIView):
    def get(self, request):
        language = Language.objects.all()
        print(language)
        serializer = LanguageSerializer(language, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateSubscription(APIView):
    authentication_classes = [StaffCustomJWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            user_id = payload.get('user_id')
            if user_id is None:
                return Response({'error': 'Staff not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                staff = Staff.objects.get(id=user_id)
            except Staff.DoesNotExist:
                return Response({"error": "Staff does not exist."}, status=status.HTTP_404_NOT_FOUND)

            try:
                mobile_number = staff.contact_no
                amount = staff.newspaper.company.subscription_amount
                count = staff.newspaper.company.recurring_count
                subscription = create_subscription(mobile_number,amount, count)
                response_body = json.loads(subscription['ResponseBody'])
                subscriptionid_data = response_body['data']
                data = Subscription(staff=staff, subscription_id=subscriptionid_data["subscriptionId"], 
                                    merchant_user_id=subscription["MerchantUserID"], 
                                    merchant_subscription_id=subscription["MerchantSubscriptionID"])
                data.save()  # Save the subscription instance
                response_data = SubscriptionSerializer(data)
                return Response({"message": "Subscription created successfully.", "data": response_data.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": "Something wrong, Please try again. Error: {}".format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
           return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)


class AuthenticateSubscription(APIView):
    authentication_classes = [StaffCustomJWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request, staff_id):
        serializer = SubscriptionAuthSerializer(data=request.data)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            user_id = payload.get('user_id')
            if user_id is None:
                return Response({'error': 'Staff not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
            
            if serializer.is_valid():
                flow_type = serializer.validated_data['flow_type']
                vpa = serializer.validated_data['vpa']
                try:
                    staff = Staff.objects.get(id=user_id)
                except Staff.DoesNotExist:
                    return Response({"error": "Staff does not exist."}, status=status.HTTP_404_NOT_FOUND)
                
                try:
                    subscription = Subscription.objects.get(staff=staff)
                except Subscription.DoesNotExist:
                    return Response({"error": "Subscription does not exist."}, status=status.HTTP_404_NOT_FOUND)

                try:
                    subscription = make_request(subscription.merchant_user_id,subscription.subscription_id, flow_type,vpa)
                    print(subscription)
                    return Response({"message": "Subscription created successfully.", "data": subscription}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"error": "Something wrong, Please try again. Error: {}".format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
           return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        
class SubscriptionStatus(APIView):
    authentication_classes = [StaffCustomJWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request, staff_id):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            user_id = payload.get('user_id')
            if user_id is None:
                return Response({'error': 'Staff not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                staff = Staff.objects.get(id=user_id)
            except Staff.DoesNotExist:
                return Response({"error": "Staff does not exist."}, status=status.HTTP_404_NOT_FOUND)

            authRequestId = request.data.get('authRequestId')
            if authRequestId is None:
                return Response({'error': 'authRequestId not found payload request,Please provide authRequestId.'}, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                # Define base URL and endpoint
                base_url = "https://mercury-t2.phonepe.com"
                endpoint_template = "/v3/recurring/auth/status/{merchantId}/{authRequestId}"

                # Dynamic values for merchantId and authRequestId
                merchantId = "AMOGHNYAONLINE"  # replace with actual merchantId
                # authRequestId = "TX7121259294"  # replace with actual authRequestId

                # Replace placeholders in the endpoint
                endpoint = endpoint_template.format(merchantId=merchantId, authRequestId=authRequestId)

                # Full URL
                url = base_url + endpoint

                # Values for saltKey and saltIndex
                saltKey = "5d8b52ef-95c2-4b00-afda-d919207624de"  # replace with actual saltKey
                saltIndex = "1"  # replace with actual saltIndex

                # Create the string to hash
                string_to_hash = f"/v3/recurring/auth/status/{merchantId}/{authRequestId}{saltKey}"

                # Generate the SHA256 hash
                hash_object = hashlib.sha256(string_to_hash.encode())
                hash_hex = hash_object.hexdigest()

                # Form the X-VERIFY header
                x_verify = f"{hash_hex}###{saltIndex}"

                # Set the headers
                headers = {
                    "Content-Type": "application/json",
                    "X-VERIFY": x_verify
                }

                # Make the GET request
                response = requests.get(url, headers=headers)

                # Print the response
                # print(f"Status Code: {response.status_code}")
                # print(f"Response Body: {response.json()}")
                response_data = {
                    "StatusCode":response.status_code,
                    "ResponseBody":response.json()
                }
                return Response({"message": "Subscription fetched successfully.", "data": response_data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": "Something wrong, Please try again. Error: {}".format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
           return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        

class SubscriptionRecurringInit(APIView):
    authentication_classes = [StaffCustomJWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request, staff_id):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = AccessToken(token)
            payload = decoded_token.payload
            user_id = payload.get('user_id')
            if user_id is None:
                return Response({'error': 'Staff not found in token payload'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                staff = Staff.objects.get(id=user_id)
            except Staff.DoesNotExist:
                return Response({"error": "Staff does not exist."}, status=status.HTTP_404_NOT_FOUND)

            amount = request.data.get('amount')
            if amount is None:
                return Response({'error': 'amount not found payload request,Please provide amount.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                subscription = Subscription.objects.get(staff=staff)
            except Subscription.DoesNotExist:
                return Response({"error": "Subscription does not exist."}, status=status.HTTP_404_NOT_FOUND)
                
            try:
                # Define base URL and endpoint
                base_url = "https://mercury-t2.phonepe.com"
                endpoint = "/v3/recurring/debit/init"

                # Dynamic values
                merchantUserId = subscription.merchant_user_id
                subscriptionId = subscription.subscription_id
                transactionId = "TX" + str(uuid.uuid4().int)[:10]  # Generate random transactionId
                amount = amount  # replace with actual value

                # Static values
                merchantId = "AMOGHNYAONLINE"  # replace with actual value
                autoDebit = True

                # Form the payload
                payload = {
                    "merchantId": merchantId,
                    "merchantUserId": merchantUserId,
                    "subscriptionId": subscriptionId,
                    "transactionId": transactionId,
                    "autoDebit": autoDebit,
                    "amount": amount
                }

                # Convert payload to JSON and then to Base64
                payload_json = json.dumps(payload)
                payload_base64 = base64.b64encode(payload_json.encode()).decode()

                # Values for saltKey and saltIndex
                saltKey = "5d8b52ef-95c2-4b00-afda-d919207624de"  # replace with actual saltKey
                saltIndex = "1"  # replace with actual saltIndex

                # Create the string to hash
                string_to_hash = payload_base64 + endpoint + saltKey

                # Generate the SHA256 hash
                hash_object = hashlib.sha256(string_to_hash.encode())
                hash_hex = hash_object.hexdigest()

                # Form the X-Verify header
                x_verify = f"{hash_hex}###{saltIndex}"

                # Set the headers
                headers = {
                    "Content-Type": "application/json",
                    "X-Verify": x_verify
                }

                # Create the request payload for sending
                request_payload = {
                    "request": payload_base64
                }

                # Full URL
                url = base_url + endpoint

                # Make the POST request
                response = requests.post(url, headers=headers, json=request_payload)

                # Print the response
                # print(f"Status Code: {response.status_code}")
                # print(f"Response Body: {response.json()}")
                # print(f"Transaction ID: {transactionId}")
                response_data = {
                    "StatusCode":response.status_code,
                    "ResponseBody":response.json(),
                    "TransactionID":transactionId
                }
                return Response({"message": "Subscription initialized successfully.", "data": response_data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": "Something wrong, Please try again. Error: {}".format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
           return Response({"error":"Something wrong,Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        
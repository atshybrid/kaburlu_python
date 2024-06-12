from django.urls import path
from .views import *



urlpatterns = [
    path('accounts/create/', CreateUserAPIView.as_view(), name='create_user'),
    path('accounts/login/', UserLoginAPIView.as_view(), name='user_login'),
    path('account/login/', UniversalUserLoginAPIView.as_view(), name='universal_user_login'),
    path('accounts/login_with_mobile/', MobileLoginAPIView.as_view(), name='login_with_mobile'),
    path('accounts/verify_otp/', VerifyOTPAPIView.as_view(), name='verify_otp'),
    path('accounts/forgot_password_request/', PasswordResetRequestAPIView.as_view(), name='forgot_password_request'),
    path('accounts/password_reset_confirm/<str:uid>/<str:token>/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    
    path('company/', CompanyAddView.as_view(), name='add_company'),
    path('company/update/<int:company_id>/', UpdateCompany.as_view(), name='company_edit'),
    path('companies/', GetAllCompanyView.as_view(), name='companies'),
    path('company/detail/<int:company_id>/', GetCompanyDetailView.as_view(), name='company_detail'),
    path('company/delete/<int:company_id>/', DeleteCompany.as_view(), name='company_delete')
]


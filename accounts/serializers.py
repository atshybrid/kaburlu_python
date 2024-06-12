from rest_framework import serializers
from .models import *



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'user_type', 'contact_number', "address", "state"]

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

class UniversalUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)

class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordConfirmSerializer(serializers.Serializer):
    # uidb64 = serializers.CharField()
    password = serializers.CharField()
    confirmPassword = serializers.CharField()
    # token = serializers.CharField()

class CompanyAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"

class CompanyLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=128, write_only=True)

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Templates
        fields = "__all__"


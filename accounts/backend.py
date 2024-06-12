from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import CustomUser




class CustomUserModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = CustomUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except user_model.DoesNotExist:
            return None
        















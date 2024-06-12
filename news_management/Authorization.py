from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from jwt import decode, exceptions

# class CustomJWTAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return None
#         token = auth_header.split(' ')[1]
#         try:
#             payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#             print(payload)
#         except exceptions.DecodeError:
#             raise AuthenticationFailed('Invalid token')
#         except exceptions.ExpiredSignatureError:
#             raise AuthenticationFailed('Token has expired')
#         company_id = payload.get('user_id')
#         if company_id is None:
#             raise AuthenticationFailed('Company ID not found in token payload')
#         return (company_id, None)


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Try to decode the token with user payload
            user_payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = user_payload.get('user_id')
            if user_id is not None:
                return (user_id, None)

        except exceptions.DecodeError:
            pass
        except exceptions.ExpiredSignatureError:
            pass

        try:
            # Try to decode the token with company payload
            company_payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            company_id = company_payload.get('company_id')
            if company_id is not None:
                return (company_id, None)

        except exceptions.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except exceptions.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        
        raise AuthenticationFailed('Invalid token')



class NewsPaperCustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ')[1]
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print(payload)
        except exceptions.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except exceptions.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        newspaper_id = payload.get('user_id')
        if newspaper_id is None:
            raise AuthenticationFailed('Company ID not found in token payload')
        return (newspaper_id, None)


class StaffCustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ')[1]
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print(payload)
        except exceptions.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except exceptions.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        staff_id = payload.get('user_id')
        if staff_id is None:
            raise AuthenticationFailed('Company ID not found in token payload')
        return (staff_id, None)


class Staff_And_Superadmin_JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Try to decode the token with user payload
            user_payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = user_payload.get('user_id')
            if user_id is not None:
                return (user_id, None)

        except exceptions.DecodeError:
            pass
        except exceptions.ExpiredSignatureError:
            pass

        try:
            # Try to decode the token with company payload
            staff_payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            staff_id = staff_payload.get('user_id')
            if staff_id is not None:
                return (staff_id, None)

        except exceptions.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except exceptions.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        
        raise AuthenticationFailed('Invalid token')
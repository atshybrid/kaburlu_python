from django.contrib import admin
from django.urls import path, include
from accounts.views import delete_project_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('', include('news_management.urls')),
    path('delete_project/', delete_project_view, name='delete_project'),
    path("django-check-seo/", include("django_check_seo.urls")),
]





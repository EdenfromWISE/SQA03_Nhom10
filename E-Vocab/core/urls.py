from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Allauth URLs for social login
    path('accounts/', include('allauth.urls')),

    # URLs cho API từ vựng
    path('api/vocabulary/', include('vocabulary.urls')),
    path('api/progress/', include('progress.urls')),
    path('api/learning/', include('learning.urls')),
    path('api/', include('chatbot.urls')),

    # Đặt routes tùy chỉnh (Google + Password Reset) LÊN TRÊN để ưu tiên
    path('api/auth/', include('students.urls')),

    # Các routes mặc định từ dj-rest-auth (login/logout/user...)
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]
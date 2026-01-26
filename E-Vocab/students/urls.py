from django.urls import path
from .views import GoogleIdTokenLoginView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('google/id-token/', GoogleIdTokenLoginView.as_view(), name='google_id_token_login'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
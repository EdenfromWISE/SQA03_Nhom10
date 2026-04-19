from django.urls import path
from .views import GoogleIdTokenLoginView, PasswordResetRequestView, PasswordResetConfirmView, UserUpdateView, UserAvatarView

urlpatterns = [
    path('google/id-token/', GoogleIdTokenLoginView.as_view(), name='google_id_token_login'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('user/update/', UserUpdateView.as_view(), name='user_update'),
    path('user/avatar/', UserAvatarView.as_view(), name='user_avatar'),
]
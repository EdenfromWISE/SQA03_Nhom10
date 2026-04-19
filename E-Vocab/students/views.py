# students/views.py

from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import UserProfile

User = get_user_model()

class GoogleIdTokenLoginView(APIView):
    def post(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        # Log request data để debug
        logger.info(f"Google login request data keys: {list(request.data.keys())}")
        
        token_id = request.data.get('id_token')
        if not token_id:
            logger.warning("Google login: ID token is missing")
            return Response({'error': 'ID token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Lấy client_id từ settings
            client_id = settings.SOCIALACCOUNT_PROVIDERS.get('google', {}).get('APP', {}).get('client_id')
            if not client_id:
                logger.error("Google login: Client ID not found in settings")
                return Response({'error': 'Google OAuth client ID not configured.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            logger.info(f"Verifying token with client_id: {client_id[:20]}...")
            
            # Verify token - xử lý lỗi clock skew
            try:
                id_info = id_token.verify_oauth2_token(
                    token_id, 
                    requests.Request(), 
                    client_id
                )
            except ValueError as token_error:
                error_msg = str(token_error)
                # Nếu là lỗi clock skew, thông báo rõ ràng cho user
                if "too early" in error_msg.lower() or "clock" in error_msg.lower():
                    import re
                    time_match = re.search(r'(\d+) < (\d+)', error_msg)
                    if time_match:
                        time_diff = int(time_match.group(2)) - int(time_match.group(1))
                        logger.warning(f"Clock skew detected ({time_diff}s): {error_msg}")
                        return Response({
                            'error': 'Clock synchronization error. Your computer\'s time is ahead of the server. Please sync your system clock and try again.',
                            'details': f'Time difference: {time_diff} seconds. {error_msg}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        logger.error(f"Clock skew error (unable to parse): {error_msg}")
                        return Response({
                            'error': 'Clock synchronization error. Please check your computer\'s time is correct.',
                            'details': error_msg
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    raise  # Nếu không phải lỗi clock skew, ném lại lỗi

            email = id_info.get('email')
            if not email:
                logger.warning("Google login: Email not found in token")
                return Response({'error': 'Email not found in token.'}, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Google login successful for email: {email}")
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': id_info.get('given_name', ''),
                    'last_name': id_info.get('family_name', ''),
                }
            )

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        except ValueError as e:
            logger.error(f"Google login: Invalid token - {str(e)}")
            return Response({'error': f'Invalid token: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            logger.error(f"Google login: Configuration error - {str(e)}")
            return Response({'error': f'Configuration error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Google login: Unexpected error - {str(e)}", exc_info=True)
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetRequestView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Respond success even if user not found to prevent email enumeration
            return Response({'message': 'If the email exists, a reset link has been sent.'})

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Build frontend reset URL if provided, else backend confirm endpoint
        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None)
        if frontend_base:
            reset_path = f"/reset-password?uid={uidb64}&token={token}"
            reset_url = f"{frontend_base.rstrip('/')}{reset_path}"
        else:
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm') + f"?uid={uidb64}&token={token}"
            )

        subject = 'Password Reset Request'
        message = f"Use the following link to reset your password: {reset_url}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

        try:
            if from_email:
                send_mail(subject, message, from_email, [email], fail_silently=True)
        except Exception:
            # Ignore email send errors in this simple implementation
            pass

        # For development convenience, return uid/token; avoid in production
        return Response({
            'message': 'If the email exists, a reset link has been sent.',
            'uid': uidb64,
            'token': token,
            'reset_url': reset_url,
        })


class PasswordResetConfirmView(APIView):
    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uidb64 or not token or not new_password:
            return Response({'error': 'uid, token and new_password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({'error': 'Invalid uid.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password has been reset successfully.'})


class UserUpdateSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(required=False, allow_null=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'age', 'avatar']

    def update(self, instance, validated_data):
        age = validated_data.pop('age', None)
        avatar = validated_data.pop('avatar', None)
        user = super().update(instance, validated_data)
        profile, created = UserProfile.objects.get_or_create(user=user)
        if age is not None:
            profile.age = age
        if avatar is not None:
            profile.avatar = avatar
        profile.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            profile = instance.userprofile
            data['age'] = profile.age
            if profile.avatar:
                data['avatar'] = profile.avatar.url
            else:
                data['avatar'] = None
        except UserProfile.DoesNotExist:
            data['age'] = None
            data['avatar'] = None
        return data


class UserUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        avatar = request.FILES.get('avatar')
        if avatar:
            profile.avatar = avatar
            profile.save()
            return Response({'avatar': profile.avatar.url}, status=status.HTTP_200_OK)
        return Response({'error': 'No avatar provided'}, status=status.HTTP_400_BAD_REQUEST)
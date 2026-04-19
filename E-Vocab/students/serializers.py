from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=False, allow_blank=True)

    def save(self, request):
        user = super().save(request)
        if not user.username:
            user.username = user.email
        user.save()
        return user
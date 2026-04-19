import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser@example.com",
        email="testuser@example.com",
        password="TestPassword123!",
    )


@pytest.fixture
def user2(db):
    return User.objects.create_user(
        username="other@example.com",
        email="other@example.com",
        password="TestPassword123!",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def auth_client2(user2):
    client = APIClient()
    refresh = RefreshToken.for_user(user2)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client

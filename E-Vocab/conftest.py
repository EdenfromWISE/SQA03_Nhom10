"""
conftest.py — Shared pytest fixtures cho toàn bộ test suite E-Vocab.

Rollback policy
---------------
Mọi test có @pytest.mark.django_db đều chạy trong một DB transaction riêng.
pytest-django tự động ROLLBACK transaction sau khi mỗi test kết thúc
(dù pass hay fail), đảm bảo dữ liệu test KHÔNG ảnh hưởng lẫn nhau và
DB luôn về trạng thái trước khi test bắt đầu.
Tham khảo: https://pytest-django.readthedocs.io/en/latest/database.html
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """APIClient không xác thực — dùng để kiểm tra anonymous access."""
    return APIClient()


@pytest.fixture
def user(db):
    """
    User thông thường dùng trong các test.
    [Rollback] Bị xoá tự động sau khi test kết thúc qua DB transaction rollback.
    """
    return User.objects.create_user(
        username="testuser@example.com",
        email="testuser@example.com",
        password="TestPassword123!",
    )


@pytest.fixture
def user2(db):
    """
    User thứ hai — dùng để kiểm tra tính cô lập dữ liệu giữa các user.
    [Rollback] Bị xoá tự động sau khi test kết thúc.
    """
    return User.objects.create_user(
        username="other@example.com",
        email="other@example.com",
        password="TestPassword123!",
    )


@pytest.fixture
def auth_client(user):
    """
    APIClient đã xác thực bằng JWT token của `user`.
    Dùng cho các endpoint yêu cầu IsAuthenticated.
    """
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def auth_client2(user2):
    """APIClient đã xác thực bằng JWT token của `user2`."""
    client = APIClient()
    refresh = RefreshToken.for_user(user2)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client

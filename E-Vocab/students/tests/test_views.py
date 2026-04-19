"""
Unit tests for students/views.py
Covers: GoogleIdTokenLoginView, PasswordResetRequestView, PasswordResetConfirmView
"""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APIClient

User = get_user_model()

GOOGLE_LOGIN_URL = "/api/auth/google/id-token/"
PASSWORD_RESET_URL = "/api/auth/password/reset/"
PASSWORD_RESET_CONFIRM_URL = "/api/auth/password/reset/confirm/"


# ─────────────────────────────────────────────────────────
# GoogleIdTokenLoginView
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGoogleIdTokenLoginView:

    def setup_method(self):
        self.client = APIClient()

    def test_UT_STU_GL_001_missing_id_token(self):
        """UT-STU-GL-001: Trả 400 khi thiếu id_token."""
        response = self.client.post(GOOGLE_LOGIN_URL, {}, format="json")
        assert response.status_code == 400
        assert "error" in response.data

    @patch("students.views.settings")
    def test_UT_STU_GL_002_missing_client_id_config(self, mock_settings):
        """UT-STU-GL-002: Trả 500 khi GOOGLE_CLIENT_ID chưa cấu hình."""
        mock_settings.SOCIALACCOUNT_PROVIDERS = {"google": {"APP": {"client_id": ""}}}
        response = self.client.post(GOOGLE_LOGIN_URL, {"id_token": "some-token"}, format="json")
        assert response.status_code == 500

    @patch("students.views.id_token.verify_oauth2_token")
    def test_UT_STU_GL_003_valid_token_creates_user_and_returns_tokens(self, mock_verify):
        """UT-STU-GL-003: Đăng nhập thành công tạo user mới, trả access + refresh."""
        mock_verify.return_value = {
            "email": "newuser@gmail.com",
            "given_name": "New",
            "family_name": "User",
        }
        response = self.client.post(GOOGLE_LOGIN_URL, {"id_token": "valid-token"}, format="json")
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert User.objects.filter(email="newuser@gmail.com").exists()

    @patch("students.views.id_token.verify_oauth2_token")
    def test_UT_STU_GL_004_valid_token_missing_email(self, mock_verify):
        """UT-STU-GL-004: Token hợp lệ nhưng payload thiếu email → 400."""
        mock_verify.return_value = {"given_name": "No", "family_name": "Email"}
        response = self.client.post(GOOGLE_LOGIN_URL, {"id_token": "valid-token"}, format="json")
        assert response.status_code == 400

    @patch("students.views.id_token.verify_oauth2_token")
    def test_UT_STU_GL_005_clock_skew_error(self, mock_verify):
        """UT-STU-GL-005: Clock skew error trả 400 với message chuyên biệt."""
        mock_verify.side_effect = ValueError("Token used too early, 1000 < 2000. Check clock")
        response = self.client.post(GOOGLE_LOGIN_URL, {"id_token": "early-token"}, format="json")
        assert response.status_code == 400
        assert "clock" in response.data.get("error", "").lower() or \
               "clock" in response.data.get("details", "").lower() or \
               "Clock" in response.data.get("error", "")

    @patch("students.views.id_token.verify_oauth2_token")
    def test_UT_STU_GL_006_invalid_token_returns_400(self, mock_verify):
        """UT-STU-GL-006: Invalid token thông thường → 400."""
        mock_verify.side_effect = ValueError("Token is invalid")
        response = self.client.post(GOOGLE_LOGIN_URL, {"id_token": "bad-token"}, format="json")
        assert response.status_code == 400
        assert "Invalid token" in response.data.get("error", "") or \
               "error" in response.data


# ─────────────────────────────────────────────────────────
# PasswordResetRequestView
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPasswordResetRequestView:

    def setup_method(self):
        self.client = APIClient()

    def test_UT_STU_PR_001_missing_email(self):
        """UT-STU-PR-001: Thiếu email → 400."""
        response = self.client.post(PASSWORD_RESET_URL, {}, format="json")
        assert response.status_code == 400

    def test_UT_STU_PR_002_nonexistent_email_returns_generic_message(self):
        """UT-STU-PR-002: Email không tồn tại → 200 với message generic (chống enumeration)."""
        response = self.client.post(
            PASSWORD_RESET_URL, {"email": "notexist@example.com"}, format="json"
        )
        assert response.status_code == 200
        assert "message" in response.data
        assert "reset" in response.data["message"].lower() or "sent" in response.data["message"].lower()

    @patch("students.views.send_mail")
    def test_UT_STU_PR_003_existing_email_returns_uid_token_reset_url(self, mock_send):
        """UT-STU-PR-003: Email tồn tại → 200 với uid, token, reset_url."""
        User.objects.create_user(
            username="reset@example.com", email="reset@example.com", password="Pass1234!"
        )
        response = self.client.post(
            PASSWORD_RESET_URL, {"email": "reset@example.com"}, format="json"
        )
        assert response.status_code == 200
        assert "uid" in response.data
        assert "token" in response.data
        assert "reset_url" in response.data


# ─────────────────────────────────────────────────────────
# PasswordResetConfirmView
# ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPasswordResetConfirmView:

    def setup_method(self):
        self.client = APIClient()

    def test_UT_STU_PC_001_missing_required_fields(self):
        """UT-STU-PC-001: Thiếu một trong uid/token/new_password → 400."""
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL, {"uid": "abc", "token": "tok"}, format="json"
        )
        assert response.status_code == 400

    def test_UT_STU_PC_002_invalid_uid(self):
        """UT-STU-PC-002: uid không decode được → 400."""
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL,
            {"uid": "!!!notbase64!!!", "token": "tok", "new_password": "newPass1!"},
            format="json",
        )
        assert response.status_code == 400
        assert "Invalid uid" in response.data.get("error", "")

    def test_UT_STU_PC_003_invalid_token(self):
        """UT-STU-PC-003: Token không hợp lệ → 400."""
        user = User.objects.create_user(
            username="tok@example.com", email="tok@example.com", password="Pass1234!"
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL,
            {"uid": uid, "token": "wrong-token", "new_password": "newPass1!"},
            format="json",
        )
        assert response.status_code == 400
        assert "Invalid or expired token" in response.data.get("error", "")

    def test_UT_STU_PC_004_valid_reset_changes_password(self):
        """UT-STU-PC-004: uid + token hợp lệ → 200, mật khẩu được đổi."""
        user = User.objects.create_user(
            username="validreset@example.com",
            email="validreset@example.com",
            password="OldPass123!",
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL,
            {"uid": uid, "token": token, "new_password": "NewPass456!"},
            format="json",
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("NewPass456!")

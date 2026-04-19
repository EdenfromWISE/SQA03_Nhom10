"""
students/tests/test_views.py
Unit tests cho students/views.py

Test Cases:
    GoogleIdTokenLoginView  : UT-STU-GL-001 → UT-STU-GL-006
    PasswordResetRequestView: UT-STU-PR-001 → UT-STU-PR-003
    PasswordResetConfirmView: UT-STU-PC-001 → UT-STU-PC-004

Rollback: pytest-django tự động rollback toàn bộ DB sau mỗi test.
"""
import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APIClient

User = get_user_model()

# ── URL constants ──────────────────────────────────────────────────────────────
GOOGLE_LOGIN_URL         = "/api/auth/google/id-token/"
PASSWORD_RESET_URL       = "/api/auth/password/reset/"
PASSWORD_RESET_CONFIRM_URL = "/api/auth/password/reset/confirm/"


# ══════════════════════════════════════════════════════════════════════════════
# GoogleIdTokenLoginView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestGoogleIdTokenLoginView:
    """Kiểm thử luồng đăng nhập bằng Google ID Token."""

    def setup_method(self):
        # Khởi tạo API client không xác thực cho từng test method
        self.client = APIClient()

    # ── UT-STU-GL-001 ──────────────────────────────────────────────────────
    def test_UT_STU_GL_001_missing_id_token(self):
        # TC: UT-STU-GL-001 — GoogleIdTokenLoginView — Thiếu id_token → HTTP 400
        # [Arrange] Không truyền id_token trong request body
        payload = {}

        # [Act]
        response = self.client.post(GOOGLE_LOGIN_URL, payload, format="json")

        # [Assert] Phải trả HTTP 400 và có field "error"
        assert response.status_code == 400
        assert "error" in response.data

        # [CheckDB] Không có user nào được tạo khi request bị reject sớm
        assert User.objects.count() == 0

    # ── UT-STU-GL-002 ──────────────────────────────────────────────────────
    @patch("students.views.settings")
    def test_UT_STU_GL_002_missing_client_id_config(self, mock_settings):
        # TC: UT-STU-GL-002 — GoogleIdTokenLoginView — GOOGLE_CLIENT_ID rỗng → HTTP 500
        # [Arrange] Mock settings để client_id trả về chuỗi rỗng
        mock_settings.SOCIALACCOUNT_PROVIDERS = {"google": {"APP": {"client_id": ""}}}

        # [Act]
        response = self.client.post(
            GOOGLE_LOGIN_URL, {"id_token": "some-token"}, format="json"
        )

        # [Assert] Phải trả HTTP 500 (lỗi cấu hình server)
        assert response.status_code == 500

        # [CheckDB] Không tạo user khi cấu hình lỗi
        assert User.objects.count() == 0

    # ── UT-STU-GL-003 ──────────────────────────────────────────────────────
    @patch("students.views.id_token.verify_oauth2_token")
    def test_UT_STU_GL_003_valid_token_creates_user_and_returns_tokens(self, mock_verify):
        # TC: UT-STU-GL-003 — GoogleIdTokenLoginView — Token hợp lệ, tạo user mới → HTTP 200
        # [Arrange] Mock Google verify trả payload hợp lệ với email mới
        new_email = "newuser@gmail.com"
        mock_verify.return_value = {
            "email": new_email,
            "given_name": "New",
            "family_name": "User",
        }

        # [Act]
        response = self.client.post(
            GOOGLE_LOGIN_URL, {"id_token": "valid-token"}, format="json"
        )

        # [Assert Response] HTTP 200 kèm access + refresh token
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

        # [CheckDB] User mới phải được tạo trong DB
        assert User.objects.filter(email=new_email).exists(), (
            f"User với email {new_email} phải được tạo sau khi đăng nhập Google thành công"
        )

    # ── UT-STU-GL-004 ──────────────────────────────────────────────────────
    @patch("students.views.id_token.verify_oauth2_token")
    def test_UT_STU_GL_004_valid_token_missing_email(self, mock_verify):
        # TC: UT-STU-GL-004 — Token hợp lệ nhưng payload thiếu field "email" → HTTP 400
        # [Arrange] Payload không có key "email"
        mock_verify.return_value = {"given_name": "No", "family_name": "Email"}

        # [Act]
        response = self.client.post(
            GOOGLE_LOGIN_URL, {"id_token": "valid-token"}, format="json"
        )

        # [Assert]
        assert response.status_code == 400

        # [CheckDB] Không tạo user khi payload thiếu email
        assert User.objects.count() == 0

    # ── UT-STU-GL-005 ──────────────────────────────────────────────────────
    @patch("students.views.id_token.verify_oauth2_token")
    def test_UT_STU_GL_005_clock_skew_error(self, mock_verify):
        # TC: UT-STU-GL-005 — Clock skew error → HTTP 400 với message chuyên biệt
        # [Arrange] Giả lập lỗi "too early" (đồng hồ máy tính lệch múi giờ)
        mock_verify.side_effect = ValueError("Token used too early, 1000 < 2000. Check clock")

        # [Act]
        response = self.client.post(
            GOOGLE_LOGIN_URL, {"id_token": "early-token"}, format="json"
        )

        # [Assert] HTTP 400 với thông điệp liên quan đến clock/time
        assert response.status_code == 400
        error_text = (
            response.data.get("error", "") + response.data.get("details", "")
        ).lower()
        assert "clock" in error_text or "time" in error_text

    # ── UT-STU-GL-006 ──────────────────────────────────────────────────────
    @patch("students.views.id_token.verify_oauth2_token")
    def test_UT_STU_GL_006_invalid_token_returns_400(self, mock_verify):
        # TC: UT-STU-GL-006 — Token không hợp lệ thông thường → HTTP 400
        # [Arrange] Giả lập ValueError thông thường (không phải clock skew)
        mock_verify.side_effect = ValueError("Token is invalid")

        # [Act]
        response = self.client.post(
            GOOGLE_LOGIN_URL, {"id_token": "bad-token"}, format="json"
        )

        # [Assert]
        assert response.status_code == 400
        assert "error" in response.data


# ══════════════════════════════════════════════════════════════════════════════
# PasswordResetRequestView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestPasswordResetRequestView:
    """Kiểm thử luồng yêu cầu đặt lại mật khẩu."""

    def setup_method(self):
        self.client = APIClient()

    # ── UT-STU-PR-001 ──────────────────────────────────────────────────────
    def test_UT_STU_PR_001_missing_email(self):
        # TC: UT-STU-PR-001 — PasswordResetRequestView — Thiếu email → HTTP 400
        # [Arrange] Body request rỗng
        # [Act]
        response = self.client.post(PASSWORD_RESET_URL, {}, format="json")

        # [Assert]
        assert response.status_code == 400
        assert "error" in response.data

    # ── UT-STU-PR-002 ──────────────────────────────────────────────────────
    def test_UT_STU_PR_002_nonexistent_email_returns_generic_message(self):
        # TC: UT-STU-PR-002 — Email không tồn tại → HTTP 200 message generic
        # Lý do: Anti-enumeration — không tiết lộ email có tồn tại hay không
        # [Arrange] Email chắc chắn không có trong DB
        nonexistent_email = "notexist@example.com"

        # [CheckDB] Xác nhận email thật sự không có trong DB
        assert not User.objects.filter(email=nonexistent_email).exists()

        # [Act]
        response = self.client.post(
            PASSWORD_RESET_URL, {"email": nonexistent_email}, format="json"
        )

        # [Assert] HTTP 200 với message chung (không phân biệt tồn tại/không)
        assert response.status_code == 200
        assert "message" in response.data

    # ── UT-STU-PR-003 ──────────────────────────────────────────────────────
    @patch("students.views.send_mail")
    def test_UT_STU_PR_003_existing_email_returns_uid_token_reset_url(self, mock_send):
        # TC: UT-STU-PR-003 — Email tồn tại → HTTP 200 có uid, token, reset_url
        # [Arrange] Tạo user với email hợp lệ trong DB
        reset_email = "reset@example.com"
        User.objects.create_user(
            username=reset_email, email=reset_email, password="Pass1234!"
        )

        # [CheckDB] Xác nhận user đã tồn tại trước khi gọi API
        assert User.objects.filter(email=reset_email).exists()

        # [Act]
        response = self.client.post(
            PASSWORD_RESET_URL, {"email": reset_email}, format="json"
        )

        # [Assert Response]
        assert response.status_code == 200
        assert "uid" in response.data, "Response phải có uid để dùng khi confirm reset"
        assert "token" in response.data, "Response phải có token để verify"
        assert "reset_url" in response.data, "Response phải có reset_url cho frontend"


# ══════════════════════════════════════════════════════════════════════════════
# PasswordResetConfirmView
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestPasswordResetConfirmView:
    """Kiểm thử luồng xác nhận đặt lại mật khẩu."""

    def setup_method(self):
        self.client = APIClient()

    # ── UT-STU-PC-001 ──────────────────────────────────────────────────────
    def test_UT_STU_PC_001_missing_required_fields(self):
        # TC: UT-STU-PC-001 — Thiếu trường bắt buộc (new_password) → HTTP 400
        # [Arrange] Chỉ truyền uid và token, thiếu new_password
        # [Act]
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL,
            {"uid": "abc", "token": "tok"},
            format="json",
        )
        # [Assert]
        assert response.status_code == 400

    # ── UT-STU-PC-002 ──────────────────────────────────────────────────────
    def test_UT_STU_PC_002_invalid_uid(self):
        # TC: UT-STU-PC-002 — uid không decode được → HTTP 400 "Invalid uid"
        # [Arrange] uid không phải base64 hợp lệ
        invalid_uid = "!!!notbase64!!!"

        # [Act]
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL,
            {"uid": invalid_uid, "token": "tok", "new_password": "newPass1!"},
            format="json",
        )

        # [Assert]
        assert response.status_code == 400
        assert "Invalid uid" in response.data.get("error", "")

    # ── UT-STU-PC-003 ──────────────────────────────────────────────────────
    def test_UT_STU_PC_003_invalid_token(self):
        # TC: UT-STU-PC-003 — uid hợp lệ nhưng token sai → HTTP 400
        # [Arrange] Tạo user, encode uid đúng, nhưng dùng token sai
        test_user = User.objects.create_user(
            username="tok@example.com", email="tok@example.com", password="Pass1234!"
        )
        valid_uid = urlsafe_base64_encode(force_bytes(test_user.pk))
        wrong_token = "this-is-a-wrong-token"

        # [CheckDB] User tồn tại trong DB
        assert User.objects.filter(email="tok@example.com").exists()

        # [Act]
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL,
            {"uid": valid_uid, "token": wrong_token, "new_password": "newPass1!"},
            format="json",
        )

        # [Assert]
        assert response.status_code == 400
        assert "Invalid or expired token" in response.data.get("error", "")

        # [CheckDB] Mật khẩu KHÔNG thay đổi khi token sai
        test_user.refresh_from_db()
        assert test_user.check_password("Pass1234!"), (
            "Mật khẩu phải GIỮ NGUYÊN khi token không hợp lệ"
        )

    # ── UT-STU-PC-004 ──────────────────────────────────────────────────────
    def test_UT_STU_PC_004_valid_reset_changes_password(self):
        # TC: UT-STU-PC-004 — uid + token hợp lệ → HTTP 200, mật khẩu đổi thành công
        # [Arrange] Tạo user, lấy uid và token hợp lệ
        old_password = "OldPass123!"
        new_password = "NewPass456!"
        test_user = User.objects.create_user(
            username="validreset@example.com",
            email="validreset@example.com",
            password=old_password,
        )
        valid_uid   = urlsafe_base64_encode(force_bytes(test_user.pk))
        valid_token = default_token_generator.make_token(test_user)

        # [CheckDB] Xác nhận mật khẩu CŨ trước khi reset
        assert test_user.check_password(old_password)

        # [Act]
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL,
            {"uid": valid_uid, "token": valid_token, "new_password": new_password},
            format="json",
        )

        # [Assert Response]
        assert response.status_code == 200

        # [CheckDB] Mật khẩu PHẢI thay đổi trong DB
        test_user.refresh_from_db()
        assert test_user.check_password(new_password), (
            "Mật khẩu mới phải được lưu vào DB sau khi reset thành công"
        )
        assert not test_user.check_password(old_password), (
            "Mật khẩu cũ không còn hợp lệ sau khi reset"
        )
        # [Rollback] pytest-django sẽ rollback user và password change sau test này

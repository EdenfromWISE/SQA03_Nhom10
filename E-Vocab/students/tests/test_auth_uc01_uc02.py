"""
students/tests/test_auth_uc01_uc02.py
Unit tests cho UC01 (Register) và UC02 (Login) — viết theo ĐẶC TẢ.

Bộ test này được xây dựng theo nguyên tắc black-box (mục 5.3.2 BG):
  "Expected output căn cứ vào thiết kế, đặc tả, không căn cứ vào source code."

Do đó, các test bên dưới có thể FAIL khi code hiện tại chưa cài đặt đầy đủ
ràng buộc trong đặc tả — đó chính là giá trị của kiểm thử hộp đen: bóc lộ
sai lệch giữa code và spec.

Test Cases:
    UC01 — Register (CustomRegisterSerializer / dj-rest-auth):
        UT-STU-RG-001 — Mật khẩu < 8 ký tự → ValidationError
        UT-STU-RG-002 — Mật khẩu thiếu chữ hoa → ValidationError
        UT-STU-RG-003 — Mật khẩu thiếu chữ thường → ValidationError
        UT-STU-RG-004 — Mật khẩu thiếu chữ số → ValidationError
        UT-STU-RG-005 — Mật khẩu thiếu ký tự đặc biệt → ValidationError
        UT-STU-RG-006 — Mật khẩu hợp lệ → tạo user thành công

    UC02 — Login (dj-rest-auth LoginView):
        UT-STU-LG-001 — Sai mật khẩu < 5 lần: response báo số lần còn lại
        UT-STU-LG-002 — Sai mật khẩu đủ 5 lần liên tiếp → tài khoản bị khóa
        UT-STU-LG-003 — Trong thời gian khóa, login đúng pw vẫn bị từ chối
        UT-STU-LG-004 — Tài khoản pending_verification → message "chưa được kích hoạt"
        UT-STU-LG-005 — Tài khoản disabled (is_active=False) → message "đã bị vô hiệu hóa"

Rollback: pytest-django tự động rollback toàn bộ DB sau mỗi test.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError

from students.serializers import CustomRegisterSerializer

User = get_user_model()


# ── URL constants ──────────────────────────────────────────────────────────────
LOGIN_URL    = "/api/auth/login/"
REGISTER_URL = "/api/auth/registration/"


def _register_payload(password: str, email: str = "newuser@example.com"):
    """Tạo payload đăng ký với password tuỳ ý."""
    return {
        "email":    email,
        "password1": password,
        "password2": password,
    }


# ══════════════════════════════════════════════════════════════════════════════
# UC01 — Register (Password complexity per spec)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestRegisterPasswordComplexity:
    """
    UC01 spec — Điều khoản nghiệp vụ:
      "Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường,
       số và ký tự đặc biệt"

    Các test bên dưới gọi thẳng CustomRegisterSerializer (không qua HTTP)
    để cô lập tầng validation.

    [Bug expected] Hiện tại core/settings.py có AUTH_PASSWORD_VALIDATORS
    bị comment toàn bộ, và CustomRegisterSerializer không thêm validator
    nào → mọi test dưới đây sẽ FAIL, bóc lộ thiếu validation theo spec.
    """

    def _is_valid(self, password: str) -> bool:
        """Helper: chạy serializer.validate() trả True nếu hợp lệ."""
        ser = CustomRegisterSerializer(data=_register_payload(password))
        return ser.is_valid()

    # ── UT-STU-RG-001 ──────────────────────────────────────────────────────
    def test_UT_STU_RG_001_password_too_short(self):
        # TC: UT-STU-RG-001 — Spec UC01: pw "ít nhất 8 ký tự".
        # pw 7 ký tự → phải bị từ chối.
        # [Arrange]
        short_pw = "Ab1!xyz"  # 7 ký tự, đủ cả 4 nhóm trừ length
        assert len(short_pw) == 7

        # [Act & Assert per spec]
        assert not self._is_valid(short_pw), (
            "Spec UC01: pw < 8 ký tự phải bị từ chối."
        )

    # ── UT-STU-RG-002 ──────────────────────────────────────────────────────
    def test_UT_STU_RG_002_password_missing_uppercase(self):
        # TC: UT-STU-RG-002 — Spec UC01: pw phải có CHỮ HOA.
        # pw chỉ có thường + số + đặc biệt → phải bị từ chối.
        no_upper = "abcdef1!"
        assert not self._is_valid(no_upper), (
            "Spec UC01: pw không có chữ hoa phải bị từ chối."
        )

    # ── UT-STU-RG-003 ──────────────────────────────────────────────────────
    def test_UT_STU_RG_003_password_missing_lowercase(self):
        # TC: UT-STU-RG-003 — Spec UC01: pw phải có CHỮ THƯỜNG.
        no_lower = "ABCDEF1!"
        assert not self._is_valid(no_lower), (
            "Spec UC01: pw không có chữ thường phải bị từ chối."
        )

    # ── UT-STU-RG-004 ──────────────────────────────────────────────────────
    def test_UT_STU_RG_004_password_missing_digit(self):
        # TC: UT-STU-RG-004 — Spec UC01: pw phải có CHỮ SỐ.
        no_digit = "Abcdefg!"
        assert not self._is_valid(no_digit), (
            "Spec UC01: pw không có chữ số phải bị từ chối."
        )

    # ── UT-STU-RG-005 ──────────────────────────────────────────────────────
    def test_UT_STU_RG_005_password_missing_special_char(self):
        # TC: UT-STU-RG-005 — Spec UC01: pw phải có KÝ TỰ ĐẶC BIỆT.
        no_special = "Abcdefg1"
        assert not self._is_valid(no_special), (
            "Spec UC01: pw không có ký tự đặc biệt phải bị từ chối."
        )

    # ── UT-STU-RG-006 ──────────────────────────────────────────────────────
    def test_UT_STU_RG_006_strong_password_accepted(self):
        # TC: UT-STU-RG-006 — Spec UC01: pw đủ 4 nhóm + 8+ ký tự → hợp lệ.
        # [Arrange] Pw chứa 8+ ký tự + chữ hoa + thường + số + đặc biệt
        strong_pw = "Strong#1Pass"

        # [Act]
        ser = CustomRegisterSerializer(
            data=_register_payload(strong_pw, email="newuser@example.com")
        )
        is_valid = ser.is_valid()

        # [Assert per spec] Pw đáp ứng đủ 4 nhóm + length → hợp lệ
        assert is_valid, (
            f"Spec UC01: pw mạnh phải hợp lệ; serializer errors={ser.errors}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# UC02 — Login (Lockout + exception flows per spec)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestLoginLockoutAndMessages:
    """
    UC02 spec — Điều khoản & ngoại lệ:
      ĐK: "Sai mật khẩu 5 lần liên tiếp sẽ khóa tài khoản 60 phút"
      E2: "Nếu sai < 5 lần: hiển thị số lần còn lại"
      E3: "5 lần sai → khóa 60 phút, set account_locked_until,
           gửi email thông báo"
      E4: "Tài khoản pending_verification → 'Tài khoản chưa được kích hoạt'"
      E5: "Tài khoản disabled → 'Tài khoản đã bị vô hiệu hóa'"

    [Bug expected] Code hiện không có view login custom, không có field
    account_locked_until trong UserProfile, không có counter sai mật khẩu
    → mọi test dưới đây sẽ FAIL, bóc lộ thiếu cài đặt theo spec.
    """

    EMAIL    = "lockuser@example.com"
    PASSWORD = "ValidPass1!"

    def setup_method(self):
        self.client = APIClient()

    def _create_user(self):
        """Tạo user hợp lệ phục vụ test."""
        return User.objects.create_user(
            username=self.EMAIL,
            email=self.EMAIL,
            password=self.PASSWORD,
        )

    def _login(self, password: str):
        """Gọi endpoint login với password tuỳ ý."""
        return self.client.post(
            LOGIN_URL,
            {"email": self.EMAIL, "password": password},
            format="json",
        )

    # ── UT-STU-LG-001 ──────────────────────────────────────────────────────
    def test_UT_STU_LG_001_wrong_password_returns_remaining_attempts(self):
        # TC: UT-STU-LG-001 — Spec UC02 E2:
        #   "Nếu sai < 5 lần: hiển thị số lần còn lại"
        # [Arrange]
        self._create_user()

        # [Act] Đăng nhập sai 1 lần
        response = self._login("WrongPass1!")

        # [Assert per spec] Response phải có thông báo về số lần thử còn lại
        assert response.status_code in (400, 401), (
            "Spec UC02 E2: sai pw phải bị từ chối."
        )
        body_text = str(response.data).lower()
        assert (
            "còn lại" in body_text
            or "remaining" in body_text
            or "lần thử" in body_text
        ), (
            "Spec UC02 E2: response phải báo số lần thử còn lại; "
            f"nhận: {response.data}"
        )

    # ── UT-STU-LG-002 ──────────────────────────────────────────────────────
    def test_UT_STU_LG_002_five_wrong_attempts_locks_account(self):
        # TC: UT-STU-LG-002 — Spec UC02 ĐK + E3:
        #   "Sai mật khẩu 5 lần liên tiếp sẽ khóa tài khoản 60 phút"
        # [Arrange]
        u = self._create_user()

        # [Act] Sai pw đủ 5 lần
        for _ in range(5):
            self._login("WrongPass1!")

        # [Assert per spec] User profile phải có field account_locked_until
        # đã được set tới thời điểm trong tương lai (~60 phút).
        u.refresh_from_db()
        profile = getattr(u, "userprofile", None)
        assert profile is not None, "User phải có UserProfile"
        assert hasattr(profile, "account_locked_until"), (
            "Spec UC02 E3: UserProfile phải có field 'account_locked_until' "
            "để đánh dấu thời điểm hết khóa."
        )
        assert profile.account_locked_until is not None, (
            "Spec UC02 E3: sau 5 lần sai, account_locked_until phải được set."
        )

    # ── UT-STU-LG-003 ──────────────────────────────────────────────────────
    def test_UT_STU_LG_003_locked_account_rejects_correct_password(self):
        # TC: UT-STU-LG-003 — Spec UC02 ĐK:
        #   Trong 60 phút khóa, login đúng pw vẫn bị từ chối.
        # [Arrange] Sai pw 5 lần để kích hoạt lock
        self._create_user()
        for _ in range(5):
            self._login("WrongPass1!")

        # [Act] Login với pw đúng
        response = self._login(self.PASSWORD)

        # [Assert per spec] phải bị từ chối với message liên quan đến khóa
        assert response.status_code in (400, 401, 403), (
            "Spec UC02: tài khoản đang khóa thì không cho login dù pw đúng."
        )
        body_text = str(response.data).lower()
        assert (
            "khóa" in body_text
            or "khoá" in body_text
            or "locked" in body_text
        ), (
            f"Spec UC02 E3: response phải nói tài khoản bị khóa; "
            f"nhận: {response.data}"
        )

    # ── UT-STU-LG-004 ──────────────────────────────────────────────────────
    def test_UT_STU_LG_004_pending_verification_account_message(self):
        # TC: UT-STU-LG-004 — Spec UC02 E4:
        #   Tài khoản pending_verification → "Tài khoản chưa được kích hoạt"
        # [Arrange] Tạo user nhưng chưa verify email (allauth EmailAddress).
        from allauth.account.models import EmailAddress
        u = self._create_user()
        EmailAddress.objects.create(
            user=u, email=self.EMAIL,
            primary=True, verified=False,
        )

        # [Act] Login với pw đúng
        response = self._login(self.PASSWORD)

        # [Assert per spec] phải bị từ chối với message kích hoạt
        assert response.status_code in (400, 401, 403), (
            "Spec UC02 E4: pending_verification không được login."
        )
        body_text = str(response.data).lower()
        assert (
            "chưa được kích hoạt" in body_text
            or "kích hoạt" in body_text
            or "not activated" in body_text
            or "verify" in body_text
        ), (
            f"Spec UC02 E4: response phải báo tài khoản chưa kích hoạt; "
            f"nhận: {response.data}"
        )

    # ── UT-STU-LG-005 ──────────────────────────────────────────────────────
    def test_UT_STU_LG_005_disabled_account_message(self):
        # TC: UT-STU-LG-005 — Spec UC02 E5:
        #   Tài khoản disabled → "Tài khoản đã bị vô hiệu hóa"
        # [Arrange] Tạo user và đánh dấu vô hiệu
        u = self._create_user()
        u.is_active = False
        u.save()

        # [Act]
        response = self._login(self.PASSWORD)

        # [Assert per spec]
        assert response.status_code in (400, 401, 403), (
            "Spec UC02 E5: tài khoản disabled không được login."
        )
        body_text = str(response.data).lower()
        assert (
            "vô hiệu hóa" in body_text
            or "vô hiệu" in body_text
            or "disabled" in body_text
        ), (
            f"Spec UC02 E5: response phải báo tài khoản đã bị vô hiệu hóa; "
            f"nhận: {response.data}"
        )

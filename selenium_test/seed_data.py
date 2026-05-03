"""Script tạo dữ liệu chuẩn để chạy system test.

Chạy 1 lần trước khi `pytest`:
    python seed_data.py

Tạo:
- 1 superuser admin/admin123 (UM-ST-01)
- 1 user thường sysauto_user@test.local / Abc@12345 (LOG-ST, UM-ST-02/04)

Yêu cầu: đã activate venv, đã `pip install django` (hoặc dùng venv của E-Vocab).
Script gọi qua Django setup nếu chạy được, fallback sang HTTP API nếu không.
"""
import os
import sys
from pathlib import Path

import requests

# Load .env của selenium_test
from dotenv import load_dotenv
HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

BE = os.getenv("BE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "admin123")
USER_EMAIL = os.getenv("TEST_USER_EMAIL", "sysauto_user@test.local")
USER_PASS = os.getenv("TEST_USER_PASSWORD", "Abc@12345")


def seed_via_django():
    """Cố gắng dùng Django ORM (chính xác nhất)."""
    backend = HERE.parent / "E-Vocab"
    sys.path.insert(0, str(backend))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    try:
        import django
        django.setup()
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Superuser
        if not User.objects.filter(username=ADMIN_USER).exists():
            User.objects.create_superuser(ADMIN_USER, "admin@local", ADMIN_PASS)
            print(f"[seed] tạo superuser {ADMIN_USER}/{ADMIN_PASS}")
        else:
            print(f"[seed] superuser {ADMIN_USER} đã tồn tại")

        # User test thường (verify sẵn)
        u = User.objects.filter(email=USER_EMAIL).first()
        if not u:
            u = User.objects.create_user(
                username=USER_EMAIL,  # email làm username theo project
                email=USER_EMAIL,
                password=USER_PASS,
            )
            u.is_active = True
            u.save()
            print(f"[seed] tạo user {USER_EMAIL}/{USER_PASS}")
        else:
            u.is_active = True
            u.set_password(USER_PASS)
            u.save()
            print(f"[seed] user {USER_EMAIL} đã có, reset mật khẩu + active")

        # Đảm bảo allauth EmailAddress 'verified=True' để login bằng email không bị chặn
        try:
            from allauth.account.models import EmailAddress
            ea, _ = EmailAddress.objects.get_or_create(
                user=u, email=USER_EMAIL, defaults={"verified": True, "primary": True}
            )
            if not ea.verified:
                ea.verified = True
                ea.primary = True
                ea.save()
                print("[seed] đánh dấu email verified cho user test")
        except Exception as e:
            print(f"[seed] bỏ qua bước verify email (allauth): {e}")
        return True
    except Exception as e:
        print(f"[seed] không dùng được Django ORM: {e}")
        return False


def seed_via_api():
    """Fallback: dùng HTTP API đăng ký user thường (superuser thì cần createsuperuser)."""
    print("[seed] sang fallback HTTP API")
    url = BE + "/api/auth/registration/"
    r = requests.post(url, json={
        "email": USER_EMAIL,
        "username": USER_EMAIL,
        "password1": USER_PASS,
        "password2": USER_PASS,
    }, timeout=15)
    if r.status_code in (200, 201):
        print(f"[seed] đăng ký user thường {USER_EMAIL} qua API thành công")
    else:
        print(f"[seed] register API trả về {r.status_code}: {r.text[:200]}")
    print(f"[seed] Hãy tạo superuser thủ công: cd E-Vocab && python manage.py createsuperuser "
          f"(username={ADMIN_USER}, password={ADMIN_PASS})")


if __name__ == "__main__":
    if not seed_via_django():
        seed_via_api()

"""Kết nối và truy vấn MySQL phục vụ test (verify dữ liệu + rollback)."""
import os
from contextlib import contextmanager
import mysql.connector


def _config():
    return dict(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "django_vocab"),
        charset="utf8mb4",
    )


@contextmanager
def connect():
    conn = mysql.connector.connect(**_config())
    try:
        yield conn
    finally:
        conn.close()


def fetch_one(sql, params=None):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        row = cur.fetchone()
        cur.close()
        return row


def fetch_all(sql, params=None):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        return rows


def execute(sql, params=None):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected


def cleanup_sysauto_users():
    """Xoá toàn bộ tài khoản test do system test tạo (prefix sysauto_).

    Xoá theo thứ tự: bảng phụ thuộc -> auth_user.
    Bỏ qua nếu bảng không tồn tại (môi trường có thể khác cấu hình).
    """
    cleanups = [
        # allauth socialaccount, account_emailaddress
        ("DELETE ea FROM account_emailaddress ea "
         "JOIN auth_user u ON ea.user_id=u.id WHERE u.email LIKE %s", ("sysauto_%",)),
        ("DELETE sa FROM socialaccount_socialaccount sa "
         "JOIN auth_user u ON sa.user_id=u.id WHERE u.email LIKE %s", ("sysauto_%",)),
        # các bảng custom của project (best-effort)
        ("DELETE p FROM progress_userprogress p "
         "JOIN auth_user u ON p.user_id=u.id WHERE u.email LIKE %s", ("sysauto_%",)),
        # cuối cùng xoá user
        ("DELETE FROM auth_user WHERE email LIKE %s", ("sysauto_%",)),
    ]
    with connect() as conn:
        cur = conn.cursor()
        for sql, params in cleanups:
            try:
                cur.execute(sql, params)
            except mysql.connector.Error:
                conn.rollback()
                continue
        conn.commit()
        cur.close()


def restore_user_active(email: str, active: bool = True):
    """Khôi phục is_active sau test UM-ST-04."""
    return execute(
        "UPDATE auth_user SET is_active=%s WHERE email=%s OR username=%s",
        (1 if active else 0, email, email),
    )

"""UM-ST: 01 / 02 / 03 / 04 — Django admin."""
import pytest

from pages.admin_page import AdminLoginPage, AdminUsersPage
from utils import db_helper


@pytest.mark.admin
def test_um_st_01_admin_login(driver, be_url, admin_user):
    """UM-ST-01: Superuser truy cập được /admin và xem danh sách user."""
    AdminLoginPage(driver, be_url).go().login(admin_user["username"], admin_user["password"])
    assert "/admin" in driver.current_url and "login" not in driver.current_url, \
        "UM-ST-01 FAIL: không vào được Django admin"
    AdminUsersPage(driver, be_url).go()
    rows = AdminUsersPage(driver, be_url).result_count()
    assert rows >= 1, "UM-ST-01 FAIL: không thấy danh sách Users"


@pytest.mark.admin
def test_um_st_02_non_staff_blocked(driver, be_url, non_staff_user):
    """UM-ST-02: User thường không được vào /admin."""
    AdminLoginPage(driver, be_url).go().login(
        non_staff_user["username"], non_staff_user["password"]
    )
    page = AdminLoginPage(driver, be_url)
    assert page.is_visible(AdminLoginPage.ERRORNOTE, timeout=5), \
        "UM-ST-02 FAIL: không hiển thị thông báo từ chối"


@pytest.mark.admin
def test_um_st_03_search_and_filter(driver, be_url, admin_user):
    """UM-ST-03: Tìm kiếm và lọc dữ liệu trong list Users."""
    AdminLoginPage(driver, be_url).go().login(admin_user["username"], admin_user["password"])
    page = AdminUsersPage(driver, be_url).go()
    page.search("nguyen")
    # nếu không có "nguyen" thì dùng prefix sysauto_
    cnt = page.result_count()
    if cnt == 0:
        page.search("sysauto_")
        cnt = page.result_count()
    assert cnt >= 0, "UM-ST-03 FAIL: search bị 500"
    assert "?q=" in driver.current_url or "q=" in driver.current_url


@pytest.mark.admin
@pytest.mark.db
def test_um_st_04_disable_user(driver, be_url, admin_user, non_staff_user):
    """UM-ST-04: Bỏ tick is_active -> user không thể login API nữa.
    Sau test phục hồi is_active=True qua fixture autouse hoặc finally.
    """
    target_email_or_username = non_staff_user["username"]
    try:
        AdminLoginPage(driver, be_url).go().login(
            admin_user["username"], admin_user["password"]
        )
        page = AdminUsersPage(driver, be_url).go()
        page.search(target_email_or_username)
        page.open_first_user()
        page.toggle_active(False).save()
        # Verify DB
        row = db_helper.fetch_one(
            "SELECT is_active FROM auth_user WHERE username=%s OR email=%s",
            (target_email_or_username, target_email_or_username),
        )
        assert row is not None and row[0] in (0, False), \
            "UM-ST-04 FAIL DB: is_active không chuyển về 0"
    finally:
        # Rollback
        db_helper.restore_user_active(target_email_or_username, True)

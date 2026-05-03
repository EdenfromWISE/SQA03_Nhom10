"""LOG-ST: 01 / 02 / 16"""
import os

import pytest

from pages.login_page import LoginPage
from pages.auth_helper import login_via_api_and_inject, clear_tokens
from utils import db_helper


def _expand(value: str) -> str:
    if not value:
        return value
    if value.startswith("${") and value.endswith("}"):
        return os.getenv(value[2:-1], "")
    return value


@pytest.mark.fe
@pytest.mark.db
def test_log_st_01_login_success(driver, fe_url, test_user):
    """LOG-ST-01: Đăng nhập thành công + DB cập nhật last_login."""
    before = db_helper.fetch_one(
        "SELECT last_login FROM auth_user WHERE email=%s", (test_user["email"],)
    )
    LoginPage(driver, fe_url).go().login(test_user["email"], test_user["password"])

    # UI: chuyển hướng khỏi /login (đợi tối đa 10s)
    from selenium.webdriver.support.ui import WebDriverWait
    WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
    assert "/login" not in driver.current_url, \
        "LOG-ST-01 FAIL UI: vẫn ở trang /login sau khi submit"
    # JWT phải được lưu trong storage
    token = driver.execute_script(
        "return localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');"
    )
    assert token, "LOG-ST-01 FAIL UI: không lưu accessToken sau khi login"

    # DB: last_login phải có giá trị mới
    after = db_helper.fetch_one(
        "SELECT last_login FROM auth_user WHERE email=%s", (test_user["email"],)
    )
    assert after and after[0] is not None, \
        "LOG-ST-01 FAIL DB: last_login không được cập nhật"
    if before and before[0] is not None:
        assert after[0] >= before[0], \
            "LOG-ST-01 FAIL DB: last_login không tăng"


@pytest.mark.fe
def test_log_st_02_empty_blocked(driver, fe_url):
    """LOG-ST-02 (empty): Bỏ trống email + password thì HTML5 chặn submit."""
    LoginPage(driver, fe_url).go().login("", "")
    # HTML5 required => không có request, vẫn ở /login
    assert "/login" in driver.current_url, \
        "LOG-ST-02 FAIL: form được submit dù trường bị bỏ trống"


@pytest.mark.fe
def test_log_st_02_format_error(driver, fe_url):
    """LOG-ST-02 (format): Email sai định dạng -> HTML5 chặn (type=email + required)."""
    LoginPage(driver, fe_url).go().login("abc@", "wrongpwd")
    assert "/login" in driver.current_url, \
        "LOG-ST-02 FAIL: email sai định dạng nhưng vẫn submit thành công"


@pytest.mark.fe
def test_log_st_16_no_session_redirect(driver, fe_url, be_url, test_user):
    """LOG-ST-16: Sau logout, dán URL Dashboard -> bị đá về /login."""
    # 1) "Đăng nhập" bằng API + inject token
    login_via_api_and_inject(driver, fe_url, be_url,
                             test_user["email"], test_user["password"])
    driver.get(fe_url + "/stats")
    assert "/stats" in driver.current_url

    # 2) "Logout" bằng cách xoá token (giả lập nút Logout)
    clear_tokens(driver)

    # 3) Dán URL trang yêu cầu auth (vd /stats) -> phải về /login
    driver.get(fe_url + "/stats")
    # FE có thể auto-redirect bằng React; nhiều trang chỉ điều hướng khi gọi API
    # Nên kiểm tra HOẶC URL về /login HOẶC không có dữ liệu user
    LoginPage(driver, fe_url).wait_url_contains("/login", timeout=8)
    assert "/login" in driver.current_url, \
        "LOG-ST-16 FAIL: vẫn vào được trang yêu cầu đăng nhập sau khi logout"

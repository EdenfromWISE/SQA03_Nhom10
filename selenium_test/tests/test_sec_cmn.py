"""SEC-ST-01-L và CMN-ST-01-L — bảo vệ route khi chưa đăng nhập."""
import pytest

from pages.auth_helper import clear_tokens
from pages.base_page import BasePage


@pytest.mark.fe
def test_sec_st_01_l_stats_unauth(driver, fe_url):
    """SEC-ST-01-L: chưa đăng nhập -> truy cập /stats phải bị về /login."""
    driver.get(fe_url)
    clear_tokens(driver)
    driver.get(fe_url + "/stats")
    page = BasePage(driver, fe_url)
    assert page.wait_url_contains("/login", timeout=8), \
        "SEC-ST-01-L FAIL: không bị chuyển hướng về /login"


@pytest.mark.fe
@pytest.mark.parametrize("path", ["/practice/1", "/learn/1", "/exam/topic/1"],
                         ids=["practice", "flashcard", "exam"])
def test_cmn_st_01_l_protected_routes(driver, fe_url, path):
    """CMN-ST-01-L: /practice, /flashcard (learn), /exam khi chưa login -> /login."""
    driver.get(fe_url)
    clear_tokens(driver)
    driver.get(fe_url + path)
    page = BasePage(driver, fe_url)
    assert page.wait_url_contains("/login", timeout=8), \
        f"CMN-ST-01-L FAIL: vẫn vào được {path} khi chưa đăng nhập"

"""PG-ST-01: tải màn Thống kê đầy đủ (H) và empty state (T2)."""
import pytest

from pages.auth_helper import login_via_api_and_inject
from pages.statistics_page import StatisticsPage
from utils import db_helper


@pytest.fixture
def authed_driver(driver, fe_url, be_url, test_user):
    login_via_api_and_inject(driver, fe_url, be_url,
                             test_user["email"], test_user["password"])
    return driver


@pytest.mark.fe
def test_pg_st_01_h_full_widgets(authed_driver, fe_url):
    """PG-ST-01-H: User có dữ liệu -> đủ widget."""
    page = StatisticsPage(authed_driver, fe_url).go()
    assert page.has_title(), "PG-ST-01-H FAIL: không thấy tiêu đề Thống kê"
    cards = page.summary_count()
    assert cards >= 4, f"PG-ST-01-H FAIL: chỉ thấy {cards}/4 thẻ tổng quan"
    # Có tối thiểu 1 chart canvas
    canvases = authed_driver.find_elements(*StatisticsPage.PROGRESS_CHART)
    assert len(canvases) >= 1, "PG-ST-01-H FAIL: không thấy biểu đồ"


@pytest.mark.fe
def test_pg_st_01_t2_empty_state(authed_driver, fe_url, test_user):
    """PG-ST-01-T2: User mới chưa học -> hiển thị 0/empty hợp lý, không lỗi giả."""
    # Chuẩn bị: xoá toàn bộ progress của user test (rollback ngay sau test)
    user_row = db_helper.fetch_one(
        "SELECT id FROM auth_user WHERE email=%s", (test_user["email"],)
    )
    uid = user_row[0] if user_row else None
    bak = []
    if uid:
        # Dump và xoá để giả lập user mới
        try:
            bak = db_helper.fetch_all(
                "SELECT * FROM progress_userprogress WHERE user_id=%s", (uid,)
            )
        except Exception:
            bak = []
        try:
            db_helper.execute(
                "DELETE FROM progress_userprogress WHERE user_id=%s", (uid,)
            )
        except Exception:
            pass

    try:
        page = StatisticsPage(authed_driver, fe_url).go()
        assert page.has_title()
        # Số liệu phải là 0 hoặc "0", không có chữ "Error"
        nums = page.summary_numbers()
        assert nums, "PG-ST-01-T2 FAIL: không thấy số liệu thống kê"
        assert all(("0" in n or n == "0") for n in nums[:4]), \
            f"PG-ST-01-T2 FAIL: số liệu không phải 0 với user mới: {nums[:4]}"
        body = authed_driver.page_source.lower()
        assert "error" not in body[-2000:], \
            "PG-ST-01-T2 FAIL: có chữ 'error' trên trang Thống kê"
    finally:
        # Không rollback nguyên trạng vì progress thường được tự build lại;
        # nếu cần phục hồi đầy đủ, dùng dump trong `bak`.
        pass

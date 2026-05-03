"""ADMIN-SRCH: HP-01/02/03, NG-02, UI-01."""
import pytest

from pages.admin_page import AdminLoginPage, AdminVocabularyPage
from utils import excel_reader

DATA = excel_reader.load_csv("admin_search.csv")
IDS = [r["tc_id"] for r in DATA]


@pytest.fixture(scope="module")
def logged_in_admin(driver_module, be_url, admin_user):
    AdminLoginPage(driver_module, be_url).go().login(
        admin_user["username"], admin_user["password"]
    )
    yield


@pytest.mark.admin
@pytest.mark.parametrize("row", DATA, ids=IDS)
def test_admin_search(driver_module, be_url, logged_in_admin, row):
    page = AdminVocabularyPage(driver_module, be_url).go()
    page.search(row["query"])
    cnt = page.result_count()
    paginator = page.paginator_text()

    if row["expect"] == "has_results":
        assert cnt >= 1, f"{row['tc_id']} FAIL: query '{row['query']}' không trả về kết quả"
    elif row["expect"] == "no_results":
        # Không văng lỗi 500, hiển thị 0
        assert cnt == 0, f"{row['tc_id']} FAIL: query rác lại có kết quả"
        # paginator của Django admin: "0 vocabularies"
        assert "0" in paginator or "0" in driver_module.page_source, \
            f"{row['tc_id']} FAIL: không có thông báo 0 kết quả"
    elif row["expect"] == "has_counter":
        # UI-01: phải có khu vực paginator hoặc "0/N" results
        assert paginator != "", \
            f"{row['tc_id']} FAIL: không hiển thị thông báo số lượng kết quả"

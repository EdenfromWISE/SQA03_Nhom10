"""REG-ST: 02 / 04 / 06 / 09 / 16"""
import pytest

from pages.register_page import RegisterPage
from utils import db_helper, excel_reader

DATA = excel_reader.load_csv("register_data.csv")
IDS = [r["tc_id"] for r in DATA]


def _user_in_db(email: str) -> bool:
    if not email:
        return False
    row = db_helper.fetch_one(
        "SELECT id FROM auth_user WHERE email=%s OR username=%s", (email, email)
    )
    return row is not None


@pytest.mark.fe
@pytest.mark.parametrize("row", DATA, ids=IDS)
def test_register(driver, fe_url, row):
    tc = row["tc_id"]
    page = RegisterPage(driver, fe_url).go()

    if tc == "REG-ST-16":
        # Nhập dở rồi back trang -> không lưu DB
        page.fill(row["email"], row["password"], row["password2"])
        driver.back()
        assert not _user_in_db(row["email"]), \
            "REG-ST-16 FAIL: dữ liệu form bị lưu vào DB dù người dùng huỷ"
        return

    page.fill(row["email"], row["password"], row["password2"])
    page.submit()

    # Validation phía client phải chặn submit (không có request thành công)
    errs = page.errors()
    assert errs, f"{tc}: Mong đợi có thông báo lỗi validation, thực tế: {errs}"

    # Đảm bảo không có user mới được tạo trong DB
    assert not _user_in_db(row["email"]), \
        f"{tc}: Validation fail nhưng vẫn tạo user trong DB"

    # Vẫn ở trang /register (không redirect /login)
    assert "/register" in driver.current_url, \
        f"{tc}: Bị chuyển trang khi validation phải chặn"

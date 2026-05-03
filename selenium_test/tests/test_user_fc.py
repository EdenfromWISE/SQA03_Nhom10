"""FLC-ST-03-H: UI-03 (lật thẻ), FLC-ST-07-L (thiếu audio)."""
import pytest

from pages.auth_helper import login_via_api_and_inject
from pages.vocabulary_page import VocabularyListPage
from utils import db_helper


@pytest.fixture
def authed_driver(driver, fe_url, be_url, test_user):
    login_via_api_and_inject(driver, fe_url, be_url,
                             test_user["email"], test_user["password"])
    return driver


@pytest.mark.fe
def test_flc_st_03_h_flip(authed_driver, fe_url, test_topic_id):
    """FLC-ST-03-H: click 'lật thẻ' -> hiện mặt sau."""
    page = VocabularyListPage(authed_driver, fe_url).go(test_topic_id)
    # Đảm bảo trang đã render flashcard
    assert page.is_visible(VocabularyListPage.FLASHCARD, timeout=10), \
        "FLC-ST-03-H FAIL: không tìm thấy flashcard"
    page.click_card()
    assert page.is_flipped(), "FLC-ST-03-H FAIL: card không chuyển sang trạng thái flipped"


@pytest.mark.fe
@pytest.mark.db
def test_flc_st_07_l_missing_audio(authed_driver, fe_url, test_topic_id):
    """FLC-ST-07-L: Từ không có audio -> nút loa phải bị disabled (kỳ vọng).
    Theo test case manual, đây là FAIL có chủ đích: hiện FE chỉ ẨN nút loa
    chứ không disable. Test sẽ khẳng định đúng kỳ vọng và do đó FAIL — phản
    ánh đúng kết quả manual test (xác nhận bug chưa fix).
    """
    # Tìm 1 topic có ít nhất 1 vocab thiếu audio_url
    row = db_helper.fetch_one(
        "SELECT topic_id FROM vocabulary_vocabulary "
        "WHERE (audio_url IS NULL OR audio_url='') LIMIT 1"
    )
    topic_id = row[0] if row else test_topic_id

    page = VocabularyListPage(authed_driver, fe_url).go(topic_id)
    assert page.is_visible(VocabularyListPage.FLASHCARD, timeout=10)

    # Nếu nút audio không tồn tại -> kỳ vọng "disabled" không thoả -> FAIL
    if not page.audio_button_present():
        pytest.fail(
            "FLC-ST-07-L FAIL (đúng manual): từ không audio thì nút loa "
            "biến mất hoàn toàn thay vì bị disabled"
        )
    # Nếu có nút thì phải bị disabled
    btns = authed_driver.find_elements(*VocabularyListPage.AUDIO_BTN_FRONT)
    assert all(not b.is_enabled() for b in btns), \
        "FLC-ST-07-L FAIL: nút loa vẫn enable cho từ thiếu audio"

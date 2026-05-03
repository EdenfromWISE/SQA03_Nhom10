"""Page Object cho Django admin (/admin)."""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class AdminLoginPage(BasePage):
    URL = "/admin/login/"
    USERNAME = (By.ID, "id_username")
    PASSWORD = (By.ID, "id_password")
    SUBMIT = (By.CSS_SELECTOR, 'input[type="submit"]')
    ERRORNOTE = (By.CSS_SELECTOR, ".errornote")

    def go(self):
        self.open(self.URL)
        return self

    def login(self, username: str, password: str):
        self.find(self.USERNAME).send_keys(username)
        self.find(self.PASSWORD).send_keys(password)
        self.find_clickable(self.SUBMIT).click()
        return self


class AdminUsersPage(BasePage):
    URL = "/admin/auth/user/"
    SEARCH_INPUT = (By.ID, "searchbar")
    RESULT_ROWS = (By.CSS_SELECTOR, "#result_list tbody tr")
    PAGINATOR = (By.CSS_SELECTOR, ".paginator")
    USER_ROW_LINK = (By.CSS_SELECTOR, "#result_list tbody tr th a")
    ACTIVE_CHECKBOX = (By.ID, "id_is_active")
    SAVE_BTN = (By.NAME, "_save")
    SUCCESS_MSG = (By.CSS_SELECTOR, "ul.messagelist .success")

    def go(self):
        self.open(self.URL)
        return self

    def search(self, q: str):
        # Đi thẳng đến URL có query để không phụ thuộc selector nút submit
        from urllib.parse import quote
        self.open(self.URL + "?q=" + quote(q))
        return self

    def result_count(self) -> int:
        try:
            rows = self.driver.find_elements(*self.RESULT_ROWS)
            return len(rows)
        except Exception:
            return 0

    def open_first_user(self):
        self.find_clickable(self.USER_ROW_LINK).click()
        return self

    def toggle_active(self, target: bool):
        cb = self.find(self.ACTIVE_CHECKBOX)
        if cb.is_selected() != target:
            cb.click()
        return self

    def save(self):
        self.find_clickable(self.SAVE_BTN).click()
        return self


class AdminVocabularyPage(BasePage):
    """Trang admin của 1 trong các model vocabulary có search-fields cho từ."""
    URL = "/admin/vocabulary/vocabulary/"
    SEARCH_INPUT = (By.ID, "searchbar")
    RESULT_ROWS = (By.CSS_SELECTOR, "#result_list tbody tr")
    EMPTY_HINT = (By.CSS_SELECTOR, ".paginator")

    def go(self):
        self.open(self.URL)
        return self

    def search(self, q: str):
        from urllib.parse import quote
        self.open(self.URL + "?q=" + quote(q))
        return self

    def result_count(self) -> int:
        return len(self.driver.find_elements(*self.RESULT_ROWS))

    def paginator_text(self) -> str:
        try:
            return self.driver.find_element(*self.EMPTY_HINT).text
        except Exception:
            return ""

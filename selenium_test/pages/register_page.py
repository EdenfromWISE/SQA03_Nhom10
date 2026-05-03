from selenium.webdriver.common.by import By
from .base_page import BasePage


class RegisterPage(BasePage):
    URL = "/register"
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    PASSWORD2 = (By.ID, "password2")
    SUBMIT = (By.CSS_SELECTOR, "button.submit-button")
    ERROR_TEXTS = (By.CSS_SELECTOR, ".error-text")
    SERVER_ERROR = (By.CSS_SELECTOR, ".error-message")

    def go(self):
        self.open(self.URL)
        return self

    def fill(self, email="", password="", password2=""):
        # Điền + blur (bằng Tab) để trigger validation real-time
        self._set(self.EMAIL, email)
        self._set(self.PASSWORD, password)
        self._set(self.PASSWORD2, password2)
        return self

    def _set(self, locator, value):
        el = self.find(locator)
        el.clear()
        if value:
            el.send_keys(value)
        # blur để validation chạy
        self.driver.execute_script("arguments[0].blur();", el)

    def submit(self):
        self.find_clickable(self.SUBMIT).click()
        return self

    def errors(self) -> list[str]:
        try:
            els = self.driver.find_elements(*self.ERROR_TEXTS)
            return [e.text.strip() for e in els if e.is_displayed()]
        except Exception:
            return []

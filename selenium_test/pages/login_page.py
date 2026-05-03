from selenium.webdriver.common.by import By
from .base_page import BasePage


class LoginPage(BasePage):
    URL = "/login"
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.CSS_SELECTOR, "button.submit-button")
    REMEMBER = (By.ID, "remember")

    def go(self):
        self.open(self.URL)
        return self

    def fill(self, email: str, password: str):
        e = self.find(self.EMAIL)
        e.clear()
        if email:
            e.send_keys(email)
        p = self.find(self.PASSWORD)
        p.clear()
        if password:
            p.send_keys(password)
        return self

    def submit(self):
        self.find_clickable(self.SUBMIT).click()
        return self

    def login(self, email, password):
        self.fill(email, password).submit()
        return self

"""Base Page Object."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException


class BasePage:
    DEFAULT_TIMEOUT = 10

    def __init__(self, driver, base_url: str = ""):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

    # ----- navigation -----
    def open(self, path: str = ""):
        url = self.base_url + (path if path.startswith("/") else "/" + path) if path else self.base_url
        self.driver.get(url)
        return self

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    # ----- helpers -----
    def find(self, locator, timeout: int | None = None):
        wait = WebDriverWait(self.driver, timeout or self.DEFAULT_TIMEOUT)
        return wait.until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator, timeout: int | None = None):
        wait = WebDriverWait(self.driver, timeout or self.DEFAULT_TIMEOUT)
        return wait.until(EC.element_to_be_clickable(locator))

    def find_all(self, locator, timeout: int | None = None):
        wait = WebDriverWait(self.driver, timeout or self.DEFAULT_TIMEOUT)
        return wait.until(EC.presence_of_all_elements_located(locator))

    def is_visible(self, locator, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def get_alert_text_and_accept(self, timeout: int = 5) -> str | None:
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            return text
        except (TimeoutException, NoAlertPresentException):
            return None

    def wait_url_contains(self, fragment: str, timeout: int = 10) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(fragment))
            return True
        except TimeoutException:
            return False

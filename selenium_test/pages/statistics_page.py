from selenium.webdriver.common.by import By
from .base_page import BasePage


class StatisticsPage(BasePage):
    URL = "/stats"
    TITLE = (By.XPATH, "//h2[contains(., 'Thống kê kết quả học tập')]")
    SUMMARY_CARDS = (By.CSS_SELECTOR, '[class*="summaryGrid"] [class*="card"]')
    NUMBER = (By.CSS_SELECTOR, '[class*="number"]')
    STREAK = (By.CSS_SELECTOR, '[class*="streakCalendar"], [class*="StreakCalendar"]')
    UPCOMING = (By.XPATH, "//*[contains(text(),'sắp ôn')]")
    PROGRESS_CHART = (By.CSS_SELECTOR, "canvas")
    RECENT = (By.XPATH, "//*[contains(text(),'phiên') or contains(text(),'gần đây')]")

    def go(self):
        self.open(self.URL)
        return self

    def has_title(self) -> bool:
        return self.is_visible(self.TITLE, timeout=8)

    def summary_count(self) -> int:
        return len(self.driver.find_elements(*self.SUMMARY_CARDS))

    def summary_numbers(self) -> list[str]:
        return [e.text.strip() for e in self.driver.find_elements(*self.NUMBER)]

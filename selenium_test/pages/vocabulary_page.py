"""Page Object cho VocabularyListPage và Flashcard (/topic/:id)."""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class VocabularyListPage(BasePage):
    BACK_BTN = (By.XPATH, "//button[contains(., 'Quay lại')]")
    FLASHCARD = (By.CSS_SELECTOR, '[class*="flashcardHorizontal"]')
    FRONT_FACE = (By.CSS_SELECTOR, '[class*="flashcardFace"][class*="front"]')
    BACK_FACE = (By.CSS_SELECTOR, '[class*="flashcardFace"][class*="back"]')
    FLIPPED = (By.CSS_SELECTOR, '[class*="flashcardHorizontal"][class*="flipped"]')
    AUDIO_BTN_FRONT = (By.CSS_SELECTOR, '[class*="flashcardRight"] [class*="audioBtn"]')
    VOCAB_ROWS = (By.CSS_SELECTOR, '[class*="vocabRow"]')
    VOCAB_WORDS = (By.CSS_SELECTOR, '[class*="vocabWord"] strong')

    def go(self, topic_id: int):
        self.open(f"/topic/{topic_id}")
        return self

    def click_card(self):
        self.find_clickable(self.FLASHCARD).click()
        return self

    def is_flipped(self) -> bool:
        return self.is_visible(self.FLIPPED, timeout=3)

    def front_displayed(self) -> bool:
        return self.is_visible(self.FRONT_FACE, timeout=3)

    def back_displayed(self) -> bool:
        return self.is_visible(self.BACK_FACE, timeout=3)

    def audio_button_present(self) -> bool:
        try:
            els = self.driver.find_elements(*self.AUDIO_BTN_FRONT)
            return any(e.is_displayed() for e in els)
        except Exception:
            return False

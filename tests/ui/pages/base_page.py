"""
Base Page Object
================
All page objects inherit from this class.
Provides shared helpers: waits, screenshots, element utilities.
"""
from __future__ import annotations
import allure
from playwright.sync_api import Page, Locator, expect


class BasePage:
    """Abstract base for all page objects."""

    URL: str = ""  # Override in subclasses

    def __init__(self, page: Page):
        self.page = page

    # ── Navigation ────────────────────────────────────────────────

    def goto(self) -> "BasePage":
        with allure.step(f"Navigate to {self.URL}"):
            self.page.goto(self.URL)
            self.page.wait_for_load_state("networkidle")
        return self

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    # ── Element Helpers ───────────────────────────────────────────

    def find(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def click(self, selector: str) -> None:
        with allure.step(f"Click: {selector}"):
            self.page.locator(selector).click()

    def fill(self, selector: str, value: str) -> None:
        with allure.step(f"Fill '{selector}' with '{value}'"):
            self.page.locator(selector).fill(value)

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def wait_for_visible(self, selector: str, timeout: int = 10_000) -> None:
        self.page.locator(selector).wait_for(state="visible", timeout=timeout)

    # ── Assertions (thin wrappers for readability) ────────────────

    def assert_url_contains(self, fragment: str) -> None:
    with allure.step(f"Assert URL contains '{fragment}'"):
        import re
        expect(self.page).to_have_url(re.compile(f".*{fragment}.*"))

    def assert_title_contains(self, text: str) -> None:
        with allure.step(f"Assert title contains '{text}'"):
            expect(self.page).to_have_title(lambda t: text in t)

    def assert_element_visible(self, selector: str) -> None:
        with allure.step(f"Assert visible: {selector}"):
            expect(self.page.locator(selector)).to_be_visible()

    def assert_element_text(self, selector: str, expected: str) -> None:
        with allure.step(f"Assert text of '{selector}' is '{expected}'"):
            expect(self.page.locator(selector)).to_have_text(expected)

    # ── Screenshots ───────────────────────────────────────────────

    def take_screenshot(self, name: str = "screenshot") -> None:
        screenshot = self.page.screenshot()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )

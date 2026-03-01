"""
Page Objects — Automation In Testing (automationintesting.online)
"""
from __future__ import annotations
import allure
from playwright.sync_api import Page, expect
from tests.ui.pages.base_page import BasePage


class HomePage(BasePage):
    URL = "https://automationintesting.online"

    # ── Selectors ─────────────────────────────────────────────────
    HERO_HEADING = "h1"
    ROOMS_CONTAINER = ".col-sm-3"
    CONTACT_FORM = "#contact"
    CONTACT_NAME = "input[name='name']"
    CONTACT_EMAIL = "input[name='email']"
    CONTACT_PHONE = "input[name='phone']"
    CONTACT_SUBJECT = "input[name='subject']"
    CONTACT_DESCRIPTION = "textarea[name='description']"
    CONTACT_SUBMIT = "button.btn.btn-outline-dark"
    COOKIE_ACCEPT = "#cookie-accept"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self) -> "HomePage":
        self.goto()
        self.page.wait_for_load_state("domcontentloaded")
        self._accept_cookie_banner()
        return self

    def _accept_cookie_banner(self) -> None:
        try:
            cookie_btn = self.page.locator(self.COOKIE_ACCEPT)
            if cookie_btn.is_visible(timeout=3000):
                cookie_btn.click()
        except Exception:
            pass

    def get_room_count(self) -> int:
        return self.page.locator(self.ROOMS_CONTAINER).count()

    def submit_contact_form(
        self, name: str, email: str, phone: str, subject: str, description: str
    ) -> None:
        with allure.step("Fill and submit contact form"):
            self.page.locator(self.CONTACT_FORM).scroll_into_view_if_needed()
            self.fill(self.CONTACT_NAME, name)
            self.fill(self.CONTACT_EMAIL, email)
            self.fill(self.CONTACT_PHONE, phone)
            self.fill(self.CONTACT_SUBJECT, subject)
            self.fill(self.CONTACT_DESCRIPTION, description)
            self.page.locator(self.CONTACT_SUBMIT).last.click()

    def assert_page_loaded(self) -> None:
        with allure.step("Assert home page is loaded"):
            expect(self.page).to_have_url("https://automationintesting.online/")
            expect(self.page.locator(self.HERO_HEADING)).to_be_visible()

    def assert_rooms_displayed(self) -> None:
        with allure.step("Assert hotel rooms are displayed"):
            self.page.wait_for_selector(self.ROOMS_CONTAINER, timeout=10000)
            expect(self.page.locator(self.ROOMS_CONTAINER).first).to_be_visible()

    def assert_contact_success(self) -> None:
        with allure.step("Assert contact form submission succeeded"):
            expect(
                self.page.get_by_text("Thanks for getting in touch")
            ).to_be_visible(timeout=15_000)


class AdminLoginPage(BasePage):
    URL = "https://automationintesting.online/#/admin"

    # ── Selectors ─────────────────────────────────────────────────
    USERNAME_INPUT = "[data-testid='username']"
    PASSWORD_INPUT = "[data-testid='password']"
    LOGIN_BUTTON = "[data-testid='submit']"
    LOGOUT_BUTTON = "button:has-text('Logout')"
    ROOMS_HEADING = "h2:has-text('Rooms')"

    def login(self, username: str = "admin", password: str = "password") -> "AdminRoomsPage":
        with allure.step(f"Login as {username}"):
            self.goto()
            self.page.wait_for_load_state("domcontentloaded")
            # Wait for React to render the form
            self.page.wait_for_selector(self.USERNAME_INPUT, timeout=15000)
            self.fill(self.USERNAME_INPUT, username)
            self.fill(self.PASSWORD_INPUT, password)
            self.click(self.LOGIN_BUTTON)
            self.page.wait_for_load_state("networkidle")
        return AdminRoomsPage(self.page)

    def login_with_invalid_credentials(self, username: str, password: str) -> None:
        with allure.step("Attempt login with invalid credentials"):
            self.goto()
            self.page.wait_for_selector(self.USERNAME_INPUT, timeout=15000)
            self.fill(self.USERNAME_INPUT, username)
            self.fill(self.PASSWORD_INPUT, password)
            self.click(self.LOGIN_BUTTON)


class AdminRoomsPage(BasePage):
    ROOMS_HEADING = "h2:has-text('Rooms')"
    LOGOUT_BUTTON = "button:has-text('Logout')"

    def assert_logged_in(self) -> None:
        with allure.step("Assert admin panel is visible after login"):
            expect(self.page.locator(self.ROOMS_HEADING)).to_be_visible(timeout=15_000)

    def logout(self) -> None:
        with allure.step("Logout"):
            self.click(self.LOGOUT_BUTTON)
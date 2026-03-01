"""
Page Objects — Automation In Testing (automationintesting.online)
=================================================================
Covers the home page and the admin login panel.
"""
from __future__ import annotations
import allure
from playwright.sync_api import Page, expect
from tests.ui.pages.base_page import BasePage


class HomePage(BasePage):
    """The main hotel booking home page."""

    URL = "https://automationintesting.online"

    # ── Selectors ─────────────────────────────────────────────────
    HERO_HEADING = "h1"
    BOOK_ROOM_BUTTON = "button:has-text('Book this room')"
    ROOMS_CONTAINER = ".hotel-room-info"
    CONTACT_FORM = "#contact"
    CONTACT_NAME = "input[data-testid='ContactName']"
    CONTACT_EMAIL = "input[data-testid='ContactEmail']"
    CONTACT_PHONE = "input[data-testid='ContactPhone']"
    CONTACT_SUBJECT = "input[data-testid='ContactSubject']"
    CONTACT_DESCRIPTION = "textarea[data-testid='ContactDescription']"
    CONTACT_SUBMIT = "button[id='submitContact']"
    CONTACT_SUCCESS = ".contact h2"
    COOKIE_ACCEPT = "#cookie-accept"

    def __init__(self, page: Page):
        super().__init__(page)

    # ── Actions ───────────────────────────────────────────────────

    def load(self) -> "HomePage":
        self.goto()
        self._accept_cookie_banner()
        return self

    def _accept_cookie_banner(self) -> None:
        cookie_btn = self.page.locator(self.COOKIE_ACCEPT)
        if cookie_btn.is_visible():
            cookie_btn.click()
            cookie_btn.wait_for(state="hidden")

    def get_room_count(self) -> int:
        return self.page.locator(self.ROOMS_CONTAINER).count()

    def submit_contact_form(
        self, name: str, email: str, phone: str, subject: str, description: str
    ) -> None:
        with allure.step("Fill and submit contact form"):
            self.fill(self.CONTACT_NAME, name)
            self.fill(self.CONTACT_EMAIL, email)
            self.fill(self.CONTACT_PHONE, phone)
            self.fill(self.CONTACT_SUBJECT, subject)
            self.fill(self.CONTACT_DESCRIPTION, description)
            self.click(self.CONTACT_SUBMIT)

    # ── Assertions ────────────────────────────────────────────────

    def assert_page_loaded(self) -> None:
        with allure.step("Assert home page is loaded"):
            expect(self.page).to_have_url(lambda url: "automationintesting.online" in url)
            expect(self.page.locator(self.HERO_HEADING)).to_be_visible()

    def assert_rooms_displayed(self) -> None:
        with allure.step("Assert hotel rooms are displayed"):
            expect(self.page.locator(self.ROOMS_CONTAINER).first).to_be_visible()

    def assert_contact_success(self) -> None:
        with allure.step("Assert contact form submission succeeded"):
            expect(self.page.locator(self.CONTACT_SUCCESS)).to_be_visible(timeout=10_000)


class AdminLoginPage(BasePage):
    """Admin panel login page."""

    URL = "https://automationintesting.online/#/admin"

    # ── Selectors ─────────────────────────────────────────────────
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#doLogin"
    LOGOUT_BUTTON = ".btn:has-text('Logout')"
    FRONT_PAGE_LINK = "a:has-text('Front Page')"
    ROOMS_HEADING = "h2:has-text('Rooms')"
    ERROR_MESSAGE = ".alert-danger"

    def login(self, username: str = "admin", password: str = "password") -> "AdminRoomsPage":
        with allure.step(f"Login as {username}"):
            self.goto()
            self.fill(self.USERNAME_INPUT, username)
            self.fill(self.PASSWORD_INPUT, password)
            self.click(self.LOGIN_BUTTON)
            self.page.wait_for_load_state("networkidle")
        return AdminRoomsPage(self.page)

    def login_with_invalid_credentials(self, username: str, password: str) -> None:
        with allure.step("Attempt login with invalid credentials"):
            self.goto()
            self.fill(self.USERNAME_INPUT, username)
            self.fill(self.PASSWORD_INPUT, password)
            self.click(self.LOGIN_BUTTON)


class AdminRoomsPage(BasePage):
    """Admin panel rooms management page (post-login)."""

    # ── Selectors ─────────────────────────────────────────────────
    ROOMS_HEADING = "h2:has-text('Rooms')"
    LOGOUT_BUTTON = "button:has-text('Logout')"
    ROOM_LISTING = ".roomlisting"

    def assert_logged_in(self) -> None:
        with allure.step("Assert admin panel is visible after login"):
            expect(self.page.locator(self.ROOMS_HEADING)).to_be_visible(timeout=15_000)

    def logout(self) -> None:
        with allure.step("Logout"):
            self.click(self.LOGOUT_BUTTON)

"""
Page Objects — Automation In Testing (automationintesting.online)
"""
from __future__ import annotations
import allure
from playwright.sync_api import Page, expect
from tests.ui.pages.base_page import BasePage


class HomePage(BasePage):
    URL = "https://automationintesting.online"

    HERO_HEADING = "h1"
    ROOMS_CONTAINER = ".room-card"
    CONTACT_FORM = "#contact"
    CONTACT_NAME = "input[data-testid='ContactName']"
    CONTACT_EMAIL = "input[data-testid='ContactEmail']"
    CONTACT_PHONE = "input[data-testid='ContactPhone']"
    CONTACT_SUBJECT = "input[data-testid='ContactSubject']"
    CONTACT_DESCRIPTION = "textarea[data-testid='ContactDescription']"
    CONTACT_SUBMIT = "button:has-text('Submit')"
    COOKIE_ACCEPT = "#cookie-accept"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self) -> "HomePage":
        self.goto()
        self.page.wait_for_load_state("networkidle")
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
            self.page.wait_for_timeout(2000)
            self.fill(self.CONTACT_NAME, name)
            self.fill(self.CONTACT_EMAIL, email)
            self.fill(self.CONTACT_PHONE, phone)
            self.fill(self.CONTACT_SUBJECT, subject)
            self.fill(self.CONTACT_DESCRIPTION, description)
            self.page.locator(self.CONTACT_SUBMIT).click()

    def assert_page_loaded(self) -> None:
        with allure.step("Assert home page is loaded"):
            expect(self.page).to_have_url("https://automationintesting.online/")
            expect(self.page.locator(self.HERO_HEADING)).to_be_visible()

    def assert_rooms_displayed(self) -> None:
        with allure.step("Assert hotel rooms are displayed"):
            self.page.wait_for_selector(self.ROOMS_CONTAINER, timeout=15000)
            expect(self.page.locator(self.ROOMS_CONTAINER).first).to_be_visible()

    def assert_contact_success(self) -> None:
        with allure.step("Assert contact form submission succeeded"):
            self.page.wait_for_timeout(3000)
            success = self.page.locator(".contact h2, .alert-success, h2").filter(
                has_text="Thanks"
            )
            expect(success).to_be_visible(timeout=15000)


class AdminLoginPage(BasePage):
    URL = "https://automationintesting.online/admin"

    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#doLogin"
    LOGOUT_BUTTON = "button:has-text('Logout')"
    ROOMS_HEADING = "h2:has-text('Rooms')"

    def login(self, username: str = "admin", password: str = "password") -> "AdminRoomsPage":
        with allure.step(f"Login as {username}"):
            self.goto()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_selector(self.USERNAME_INPUT, timeout=20000)
            self.fill(self.USERNAME_INPUT, username)
            self.fill(self.PASSWORD_INPUT, password)
            self.click(self.LOGIN_BUTTON)
            self.page.wait_for_load_state("networkidle")
        return AdminRoomsPage(self.page)

    def login_with_invalid_credentials(self, username: str, password: str) -> None:
        with allure.step("Attempt login with invalid credentials"):
            self.goto()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_selector(self.USERNAME_INPUT, timeout=20000)
            self.fill(self.USERNAME_INPUT, username)
            self.fill(self.PASSWORD_INPUT, password)
            self.click(self.LOGIN_BUTTON)


class AdminRoomsPage(BasePage):
    ROOMS_HEADING = "h2:has-text('Rooms')"
    LOGOUT_BUTTON = "button:has-text('Logout')"

    def assert_logged_in(self) -> None:
        with allure.step("Assert admin panel is visible after login"):
            expect(self.page.locator(self.ROOMS_HEADING)).to_be_visible(timeout=15000)

    def logout(self) -> None:
        with allure.step("Logout"):
            self.click(self.LOGOUT_BUTTON)
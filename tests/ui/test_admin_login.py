"""
UI Tests — Admin Login Panel
=============================
Validates authentication flows for the admin panel UI.
"""
import pytest
import allure
from faker import Faker

from tests.ui.pages.home_page import AdminLoginPage

fake = Faker()


@allure.feature("Admin Panel")
@allure.story("Login")
class TestAdminLogin:

    @allure.title("Valid admin credentials redirect to rooms dashboard")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_valid_admin_login(self, admin_login_page: AdminLoginPage):
        rooms_page = admin_login_page.login()
        rooms_page.assert_logged_in()
        rooms_page.take_screenshot("admin-logged-in")

    @allure.title("Admin panel URL is accessible")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_admin_login_page_loads(self, admin_login_page: AdminLoginPage):
        admin_login_page.goto()
        admin_login_page.assert_element_visible(AdminLoginPage.USERNAME_INPUT)
        admin_login_page.assert_element_visible(AdminLoginPage.PASSWORD_INPUT)
        admin_login_page.assert_element_visible(AdminLoginPage.LOGIN_BUTTON)
        admin_login_page.take_screenshot("admin-login-page")

    @allure.title("Login and logout cycle works correctly")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.ui
    def test_login_and_logout(self, admin_login_page: AdminLoginPage):
        rooms_page = admin_login_page.login()
        rooms_page.assert_logged_in()
        rooms_page.logout()
        # After logout, login button should reappear
        admin_login_page.assert_element_visible(AdminLoginPage.LOGIN_BUTTON)

    @allure.title("Invalid credentials do not grant access")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.ui
    def test_invalid_login_rejected(self, admin_login_page: AdminLoginPage):
        admin_login_page.login_with_invalid_credentials(
            username=fake.user_name(),
            password=fake.password(),
        )
        # Should still be on the login page
        admin_login_page.assert_element_visible(AdminLoginPage.LOGIN_BUTTON)
        admin_login_page.take_screenshot("invalid-login-rejected")

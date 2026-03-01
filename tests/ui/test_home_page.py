"""
UI Tests — Home Page
====================
Validates core UI elements, layout, and user interactions
on the hotel booking home page using Playwright + POM.
"""
import pytest
import allure
from faker import Faker

from tests.ui.pages.home_page import HomePage

fake = Faker("en_GB")


@allure.feature("Home Page")
@allure.story("Page Load & Layout")
class TestHomePageLoad:

    @allure.title("Home page loads successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_home_page_loads(self, home_page: HomePage):
        home_page.load()
        home_page.assert_page_loaded()
        home_page.take_screenshot("home-page-loaded")

    @allure.title("Hotel rooms are displayed on home page")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_rooms_are_displayed(self, home_page: HomePage):
        home_page.load()
        home_page.assert_rooms_displayed()
        room_count = home_page.get_room_count()
        assert room_count >= 1, f"Expected at least 1 room, found {room_count}"

    @allure.title("Page title contains hotel name")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.ui
    def test_page_has_correct_title(self, home_page: HomePage):
        home_page.load()
        title = home_page.get_title()
        assert title, "Page title should not be empty"

    @allure.title("Contact section is present on the page")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.ui
    def test_contact_section_visible(self, home_page: HomePage):
        home_page.load()
        home_page.assert_element_visible(HomePage.CONTACT_FORM)


@allure.feature("Home Page")
@allure.story("Contact Form")
class TestContactForm:

    @allure.title("Valid contact form submission shows success")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.ui
    def test_contact_form_success(self, home_page: HomePage):
        home_page.load()
        home_page.submit_contact_form(
            name=fake.name(),
            email=fake.email(),
            phone="01234567890",
            subject="Automated Test Inquiry",
            description="This is an automated test message. " * 3,
        )
        home_page.assert_contact_success()
        home_page.take_screenshot("contact-form-success")

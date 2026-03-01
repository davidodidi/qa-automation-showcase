"""
UI Test Fixtures — Playwright
==============================
Browser and page fixtures scoped for optimal speed.
Screenshots are captured automatically on failure.
"""
from __future__ import annotations
import pytest
import allure
from playwright.sync_api import Page

from config.settings import settings
from tests.ui.pages.home_page import HomePage, AdminLoginPage


# ── Browser Configuration ─────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Override default browser context settings."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "en-GB",
        "timezone_id": "Europe/London",
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Control headless mode and slow-mo from settings."""
    return {
        **browser_type_launch_args,
        "headless": settings.headless,
        "slow_mo": settings.slow_mo,
    }


# ── Auto-screenshot on Failure ────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(page: Page, request):
    """Automatically attach a screenshot to Allure report when a test fails."""
    yield
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        screenshot = page.screenshot()
        allure.attach(
            screenshot,
            name=f"FAILURE — {request.node.name}",
            attachment_type=allure.attachment_type.PNG,
        )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ── Page Object Fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def admin_login_page(page: Page) -> AdminLoginPage:
    return AdminLoginPage(page)

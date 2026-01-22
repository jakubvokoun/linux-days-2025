import os
import pytest
import time
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_reditect_to_login(page: Page):
    response = page.goto(BASE_URL)
    # page.pause()
    page.screenshot(path="login.png")
    time.sleep(2)
    assert response.url.endswith("/login")


def test_page_title(page: Page):
    page.goto(f"{BASE_URL}/login")
    time.sleep(2)
    expect(page).to_have_title("Login - Ping CRM")


def test_page_heading(page: Page):
    page.goto(f"{BASE_URL}/login")
    heading = page.locator("h1")
    time.sleep(2)
    expect(heading).to_have_text("Welcome Back!")


def test_login_fails(page: Page):
    page.goto(f"{BASE_URL}/login")
    page.get_by_label("Email:").fill("x@x.com")
    page.get_by_label("Password:").fill("x")
    page.get_by_role("button").click()
    error_msg = page.locator(".form-error")
    time.sleep(2)
    expect(error_msg).to_have_text("These credentials do not match our records.")


def test_login_is_ok(page: Page):
    page.goto(f"{BASE_URL}/login")
    page.get_by_role("button").click()
    heading = page.locator("h1")
    time.sleep(2)
    expect(heading).to_have_text("Dashboard")

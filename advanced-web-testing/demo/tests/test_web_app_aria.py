import os
import pytest
import time
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_aira(page: Page):
    page.goto(f"{BASE_URL}/login")
    time.sleep(2)
    expect(page.locator("form")).to_match_aria_snapshot("""
- heading "Welcome Back!" [level=1]
- text: "Email:"
- textbox "Email:": johndoe@example.com
- text: "Password:"
- textbox "Password:": secret
- checkbox "Remember Me"
- text: "Remember Me"
- button "Login"
""")

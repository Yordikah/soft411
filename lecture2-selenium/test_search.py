"""Lecture 2 - First Selenium tests.

Test 1 is the sample from the lecture (open selenium.dev, check the title).
Tests 2-3 do a real user action on Selenium's own demo form:
type into a field, click Submit, and check the result message.
"""
import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

FORM_URL = "https://www.selenium.dev/selenium/web/web-form.html"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    if os.environ.get("CI"):                 # GitHub Actions has no screen
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)                    # wait up to 5 s for elements
    yield drv
    drv.quit()


def test_selenium_homepage_title(driver):
    # sample code from the lecture slide
    driver.get("https://www.selenium.dev/")
    assert "Selenium" in driver.title


def test_submit_web_form(driver):
    driver.get(FORM_URL)
    assert driver.title == "Web form"

    text_box = driver.find_element(By.NAME, "my-text")
    text_box.send_keys("Yordanos")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    message = driver.find_element(By.ID, "message")
    assert message.text == "Received!"
    os.makedirs("screenshots", exist_ok=True)
    driver.save_screenshot("screenshots/form_submitted.png")


def test_typed_text_is_kept_in_field(driver):
    driver.get(FORM_URL)
    text_box = driver.find_element(By.ID, "my-text-id")
    text_box.send_keys("SOFT411")
    assert text_box.get_attribute("value") == "SOFT411"

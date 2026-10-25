# SOFT411 – Lecture 2: First Selenium Test

`test_search.py` contains three browser tests written with Selenium WebDriver + pytest:

1. **test_selenium_homepage_title** – the sample from the lecture: opens selenium.dev and checks the title contains "Selenium".
2. **test_submit_web_form** – opens Selenium's demo web form, types a name, clicks **Submit**, and checks the message "Received!".
3. **test_typed_text_is_kept_in_field** – types into the text field and checks the field really contains the text.

## Run it on your computer
```bash
pip install selenium pytest
cd lecture2-selenium
python -m pytest -v
```
Chrome opens and you can watch the steps. In GitHub Actions the same tests run in headless Chrome (workflow: `.github/workflows/lecture2.yml`).

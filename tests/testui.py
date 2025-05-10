import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="module")
def browser():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    yield driver
    driver.quit()

def test_app_launches(browser):
    browser.get("http://localhost:8501")  # default Streamlit port
    assert "Document QA Assistant" in browser.title
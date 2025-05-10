import subprocess, time, pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="module")
def live_app():
    # 1) Launch Streamlit in headless mode on port 8501
    proc = subprocess.Popen(
        ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.headless=true"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(5)  # give it a moment to spin up
    yield
    proc.terminate()
    proc.wait()

@pytest.fixture(scope="module")
def driver():
    # 2) Configure headless Chrome
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=opts)
    yield driver
    driver.quit()

def test_health(live_app, driver):
    url = "http://localhost:8501"
    driver.get(url)

    # 3) Wait up to 10 seconds for the title to update
    for _ in range(20):
        if "Document QA Assistant" in driver.title:
            break
        time.sleep(0.5)
    assert "Document QA Assistant" in driver.title

    # 4) Confirm subheader is rendered (Streamlit renders subheaders as <h2>)
    # wait up to 10s for any element containing the exact text
    sub = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Chat with Doc Assist')]")
        )
    )
    assert "Chat with Doc Assist" in sub.text
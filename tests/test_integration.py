import subprocess
import time
import pytest
import requests

@pytest.fixture(scope="module")
def live_app():
    # start streamlit app in background
    proc = subprocess.Popen(
        ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # wait for server
    time.sleep(5)
    yield
    proc.terminate()
    proc.wait()

def test_health(live_app):
    r = requests.get("http://localhost:8501")
    assert r.status_code == 200
    assert "Document QA Assistant" in r.text
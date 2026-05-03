"""Fixture chung: load env, driver Selenium, hook chụp ảnh khi fail, rollback DB."""
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Load .env (nếu có) trước mọi thứ
load_dotenv(ROOT / ".env")

from utils import db_helper  # noqa: E402


# -------- Cấu hình URL & DB cho test --------
@pytest.fixture(scope="session")
def fe_url():
    return os.getenv("FE_BASE_URL", "http://localhost:5173").rstrip("/")


@pytest.fixture(scope="session")
def be_url():
    return os.getenv("BE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture(scope="session")
def test_user():
    return {
        "email": os.getenv("TEST_USER_EMAIL", "sysauto_user@test.local"),
        "password": os.getenv("TEST_USER_PASSWORD", "Abc@12345"),
    }


@pytest.fixture(scope="session")
def admin_user():
    return {
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "admin123"),
    }


@pytest.fixture(scope="session")
def non_staff_user():
    return {
        "username": os.getenv("NON_STAFF_USERNAME", "sysauto_user"),
        "password": os.getenv("NON_STAFF_PASSWORD", "Abc@12345"),
    }


@pytest.fixture(scope="session")
def test_topic_id():
    return int(os.getenv("TEST_TOPIC_ID", "1"))


# -------- Selenium driver --------
def _detect_browser() -> str:
    """Auto-detect browser nếu BROWSER env không set hoặc set 'auto'."""
    forced = os.getenv("BROWSER", "auto").strip().lower()
    if forced in ("chrome", "edge"):
        return forced
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    if any(os.path.isfile(p) for p in chrome_paths):
        return "chrome"
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    if any(os.path.isfile(p) for p in edge_paths):
        return "edge"
    return "chrome"  # fallback, sẽ báo lỗi rõ ràng nếu không có


def _build_browser():
    """Tạo Selenium driver. Mặc định dùng Selenium Manager (built-in từ Selenium 4.10+)
    để Selenium tự download driver tương ứng — không phụ thuộc webdriver-manager.
    """
    headless = os.getenv("HEADLESS", "0") == "1"
    name = _detect_browser()
    if name == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1366,900")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=vi-VN")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        # Selenium Manager tự lo driver
        return webdriver.Edge(options=options)
    # default Chrome
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--lang=vi-VN")
    return webdriver.Chrome(options=options)


@pytest.fixture
def driver():
    drv = _build_browser()
    drv.implicitly_wait(0)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture(scope="module")
def driver_module():
    drv = _build_browser()
    drv.implicitly_wait(0)
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


# -------- Rollback dữ liệu test sau session --------
@pytest.fixture(scope="session", autouse=True)
def cleanup_after_session():
    yield
    try:
        db_helper.cleanup_sysauto_users()
        # Đảm bảo user dùng cho LOG-ST tồn tại sẽ được restore active=1
        if os.getenv("TEST_USER_EMAIL"):
            db_helper.restore_user_active(os.getenv("TEST_USER_EMAIL"), True)
    except Exception as e:
        print(f"[cleanup] bỏ qua lỗi DB rollback: {e}")


# -------- Hook chụp ảnh khi test fail --------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            shots = ROOT / "reports" / "screenshots"
            shots.mkdir(parents=True, exist_ok=True)
            fname = f"{item.name}.png".replace("[", "_").replace("]", "_").replace("/", "_")
            path = shots / fname
            try:
                drv.save_screenshot(str(path))
                meta_path = path.with_suffix(".txt")
                try:
                    cur_url = drv.current_url
                except Exception as e:
                    cur_url = f"<error: {e}>"
                try:
                    cur_title = drv.title
                except Exception as e:
                    cur_title = f"<error: {e}>"
                try:
                    body_text = drv.execute_script(
                        "return (document.body && document.body.innerText || '').slice(0, 800);"
                    )
                except Exception as e:
                    body_text = f"<error: {e}>"
                try:
                    storage = drv.execute_script(
                        "return JSON.stringify({"
                        "ls_access: localStorage.getItem('accessToken'),"
                        "ss_access: sessionStorage.getItem('accessToken'),"
                        "path: location.pathname});"
                    )
                except Exception as e:
                    storage = f"<error: {e}>"
                with open(meta_path, "w", encoding="utf-8") as f:
                    f.write(f"URL: {cur_url}\n")
                    f.write(f"TITLE: {cur_title}\n")
                    f.write(f"STORAGE: {storage}\n")
                    f.write("BODY (first 800 chars):\n")
                    f.write(str(body_text))
                # Đính kèm vào pytest-html report nếu có
                try:
                    from pytest_html import extras  # type: ignore
                    extra = getattr(rep, "extras", [])
                    extra.append(extras.image(str(path.relative_to(ROOT / "reports"))))
                    rep.extras = extra
                except Exception:
                    pass
                print(f"[screenshot] {path}")
                print(f"[screenshot] URL={cur_url}")
            except Exception as e:
                print(f"[screenshot] không chụp được: {e}")

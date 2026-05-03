"""Helper login-by-API + inject token để test bỏ qua màn login khi cần."""
import requests
from selenium.webdriver.remote.webdriver import WebDriver


def api_login(be_url: str, email: str, password: str) -> dict:
    url = be_url.rstrip("/") + "/api/auth/login/"
    r = requests.post(url, json={"email": email, "password": password}, timeout=15)
    r.raise_for_status()
    return r.json()


def inject_tokens(driver: WebDriver, fe_url: str, tokens: dict, remember: bool = True):
    """Mở FE rồi nhét token vào localStorage/sessionStorage để pass auth."""
    driver.get(fe_url)
    storage = "localStorage" if remember else "sessionStorage"
    access = tokens.get("access") or tokens.get("access_token") or tokens.get("token") or ""
    refresh = tokens.get("refresh") or ""
    driver.execute_script(
        f"window.{storage}.setItem('accessToken', arguments[0]);"
        f"if (arguments[1]) window.{storage}.setItem('refreshToken', arguments[1]);",
        access, refresh,
    )
    if remember:
        driver.execute_script("localStorage.setItem('rememberMe','1');")


def clear_tokens(driver: WebDriver):
    driver.execute_script(
        "['accessToken','refreshToken','rememberMe'].forEach(k=>{"
        "localStorage.removeItem(k);sessionStorage.removeItem(k);});"
    )


def login_via_api_and_inject(driver, fe_url, be_url, email, password, remember=True):
    tokens = api_login(be_url, email, password)
    inject_tokens(driver, fe_url, tokens, remember=remember)
    return tokens

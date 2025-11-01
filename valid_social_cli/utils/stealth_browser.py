# utils/stealth_browser.py
import os
from typing import Optional, Tuple
from playwright.sync_api import sync_playwright, Playwright, BrowserContext


STEALTH_JS = r"""
// Minimal stealth patches. These reduce common automation signals.
// Note: This is helpful but not bulletproof.
Object.defineProperty(navigator, 'webdriver', { get: () => false });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
const origQuery = navigator.permissions.query;
navigator.permissions.query = (parameters) =>
  parameters.name === 'notifications'
    ? Promise.resolve({ state: Notification.permission })
    : origQuery(parameters);
"""


def ensure_profile_dir(path: str) -> str:
    """Return absolute path and ensure it exists."""
    path = os.path.abspath(path)
    os.makedirs(path, exist_ok=True)
    return path


def launch_stealth_browser(
    user_data_dir: str = "storage/browser_profiles/chrome",
    headless: bool = False,
    slow_mo: int = 80,
    user_agent: Optional[str] = None
) -> Tuple[Playwright, BrowserContext]:
    """
    Launch a persistent Chrome context with basic stealth patches.
    Closes all existing tabs first before returning the context.

    Returns:
        (playwright, context) where `context` is a BrowserContext (persistent).
    """
    user_data_dir = ensure_profile_dir(user_data_dir)

    playwright = sync_playwright().start()

    if user_agent is None:
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/117.0.0.0 Safari/537.36"
        )

    context = playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        channel="chrome",
        headless=headless,
        slow_mo=slow_mo,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
        viewport={"width": 1280, "height": 800},
        user_agent=user_agent,
    )

    # Close all existing pages/tabs
    for page in context.pages:
        page.close()

    # Add stealth JS to the context
    context.add_init_script(STEALTH_JS)

    return playwright, context


def save_session(context: BrowserContext, path: str) -> None:
    """
    Save Playwright storage_state (cookies + localStorage) to JSON.
    Use this after manual login to persist session for later automated runs.
    """
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    context.storage_state(path=path)


def close_playwright(playwright: Playwright, context: BrowserContext) -> None:
    """Close context and stop Playwright gracefully."""
    try:
        context.close()
    finally:
        playwright.stop()

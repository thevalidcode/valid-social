"""
Robust, type-safe Playwright stealth browser helper that ALWAYS uses
Playwright's bundled Chromium (no system Chrome), applies heavy stealth
patches, supports persistent profile storage, and works cross-platform.

Usage:
    playwright, context = launch_stealth_browser()
    page = context.new_page()
    page.goto("https://x.com", wait_until="domcontentloaded")
    ...
    save_session(context, "storage/sessions/x_session.json")
    close_playwright(playwright, context)
"""

from __future__ import annotations

import os
import platform
import traceback
from typing import Optional, Tuple, List
from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Error

# ---- STEALTH JS ----
# Injected before any page loads. Covers common detection vectors.
STEALTH_INIT_SCRIPT: str = r"""
// Minimal but deep stealth patches.
// 1) navigator.webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => false });

// 2) languages
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

// 3) plugins
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4] });

// 4) permissions.query override (notifications)
const _origPermissionsQuery = navigator.permissions && navigator.permissions.query;
if (_origPermissionsQuery) {
  navigator.permissions.query = (params) => {
    if (params && params.name === 'notifications') {
      return Promise.resolve({ state: Notification.permission });
    }
    return _origPermissionsQuery(params);
  };
}

// 5) window.chrome shim
window.chrome = window.chrome || { runtime: {} };

// 6) hardwareConcurrency and deviceMemory
if (!navigator.hardwareConcurrency) {
  Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
}
if (!navigator.deviceMemory) {
  Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
}

// 7) webdriver property on document (some checks)
Object.defineProperty(document, 'webdriver', { get: () => undefined });

// 8) plugins enumeration trick
const _origNavigatorPlugins = navigator.plugins;
if (!_origNavigatorPlugins || _origNavigatorPlugins.length === 0) {
  Object.defineProperty(navigator, 'plugins', { get: () => [{name:'Chrome PDF Plugin'},{name:'Chrome PDF Viewer'}] });
}

// 9) emulate chrome.runtime.toString for some checks
if (!window.chrome || !window.chrome.runtime) {
  window.chrome = window.chrome || { runtime: {} };
}
if (window.chrome && window.chrome.runtime && !window.chrome.runtime.toString) {
  window.chrome.runtime.toString = function() { return '[object ChromeRuntime]'; };
}

// 10) fix userAgent vendor/platform if needed (done server-side via Playwright context)
"""

# ---- Helper utilities ----


def ensure_profile_dir(path: str) -> str:
    """
    Ensure the provided path exists and return its absolute path.
    """
    abs_path = os.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def default_user_data_dir(prefix: str = "chromium") -> str:
    """
    Build a safe per-user, per-platform profile folder path.
    """
    username = os.getenv("USERNAME") or os.getenv("USER") or "user"
    system = platform.system().lower()
    base = os.path.join("storage", "browser_profiles")
    path = os.path.join(base, f"{prefix}_{system}_{username}")
    return ensure_profile_dir(path)

# ---- Main launcher (always uses Playwright bundled Chromium) ----


def launch_stealth_browser(
    user_data_dir: Optional[str] = None,
    headless: bool = False,
    slow_mo: int = 60,
    user_agent: Optional[str] = None,
    # ignored: we always use bundled Chromium for reliability
    prefer_system_chrome: bool = False,
) -> Tuple[Playwright, BrowserContext]:
    """
    Launch Playwright bundled Chromium with stealth patches and a persistent context.

    Returns:
        (playwright, context)
    """
    if user_data_dir is None:
        user_data_dir = default_user_data_dir(prefix="chromium")

    # Sanitize and ensure profile dir
    user_data_dir = ensure_profile_dir(user_data_dir)

    playwright: Playwright = sync_playwright().start()

    system = platform.system()

    # Sensible default user agent per platform (can be overridden)
    if user_agent is None:
        if system == "Darwin":
            user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
        elif system == "Linux":
            user_agent = ("Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
        else:  # Windows and others
            user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")

    # Construct safe args. Keep them conservative for Windows.
    args: List[str] = [
        "--disable-blink-features=AutomationControlled",
        "--disable-web-security",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=site-per-process",  # reduces some iframe issues
    ]

    # Linux container tweaks if needed
    if system == "Linux":
        args += ["--no-sandbox", "--disable-dev-shm-usage"]

    try:
        # Always use Playwright's bundled Chromium (no executable_path)
        context: BrowserContext = playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            slow_mo=slow_mo,
            args=args,
            viewport={"width": 1280, "height": 800},
            user_agent=user_agent,
        )

        # close default blank pages if any
        for p in list(context.pages):
            try:
                p.close()
            except Exception:
                pass

        # inject stealth before any navigations
        context.add_init_script(STEALTH_INIT_SCRIPT)

        # Final debug print
        print(
            f"✅ Launched Playwright bundled Chromium. user_data_dir={user_data_dir}")
        return playwright, context

    except Exception as exc:
        # Ensure Playwright is stopped and bubble up after diagnostic
        print("❌ Failed launching Playwright bundled Chromium. Traceback follows:")
        traceback.print_exc()
        try:
            playwright.stop()
        except Exception:
            pass
        raise exc

# ---- Session helpers ----


def close_playwright(
    playwright: Playwright,
    context: Optional[BrowserContext],
    show_errors: bool = True
) -> None:
    """
    Safely close the browser context and stop Playwright.
    Can be called multiple times without raising errors.
    """
    # Close the browser context
    if context is not None:
        try:
            context.close()
            if show_errors:
                print("✅ Browser context closed successfully.")
        except Error as e:
            # Ignore "Event loop is closed" errors
            if "Event loop is closed" in str(e):
                if show_errors:
                    print("ℹ️ Browser context already closed (event loop closed).")
            else:
                if show_errors:
                    print("⚠️ Error when closing browser context:")
                    traceback.print_exc()
        except Exception:
            if show_errors:
                print("⚠️ Unexpected error when closing browser context:")
                traceback.print_exc()

    # Stop Playwright
    try:
        playwright.stop()
        if show_errors:
            print("✅ Playwright stopped successfully.")
    except Error as e:
        if "Event loop is closed" in str(e):
            if show_errors:
                print("ℹ️ Playwright already stopped (event loop closed).")
        else:
            if show_errors:
                print("⚠️ Error when stopping Playwright:")
                traceback.print_exc()
    except Exception:
        if show_errors:
            print("⚠️ Unexpected error when stopping Playwright:")
            traceback.print_exc()

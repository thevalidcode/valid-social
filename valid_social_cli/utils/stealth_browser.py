import os
import platform
import traceback
import shutil
import getpass
from typing import Optional, Tuple, List
from pathlib import Path
from playwright.sync_api import sync_playwright, Playwright, BrowserContext

STEALTH_JS: str = r"""
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
    path = os.path.abspath(path)
    os.makedirs(path, exist_ok=True)
    return path


def _candidate_chrome_paths() -> List[str]:
    candidates: List[str] = []

    # If Chrome is on PATH
    which_path = shutil.which("chrome") or shutil.which(
        "chrome.exe") or shutil.which("google-chrome")
    if which_path:
        candidates.append(which_path)

    # Typical Program Files locations
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    local_appdata = os.environ.get(
        "LOCALAPPDATA", str(Path.home() / "AppData/Local"))

    candidates += [
        os.path.join(pf, "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(pf86, "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(local_appdata, "Programs", "Google",
                     "Chrome", "Application", "chrome.exe"),
    ]

    # Deduplicate
    seen: set[str] = set()
    out: List[str] = []
    for p in candidates:
        if p and p not in seen:
            out.append(p)
            seen.add(p)
    return out


def _find_chrome_executable() -> Optional[str]:
    """
    Return system Chrome executable path if available.
    """
    for path in _candidate_chrome_paths():
        try:
            path_expanded = os.path.expandvars(path)
            if os.path.isfile(path_expanded) and os.access(path_expanded, os.X_OK):
                return path_expanded
        except Exception:
            continue
    return None


def launch_stealth_browser(
    user_data_dir: Optional[str] = None,
    headless: bool = False,
    slow_mo: int = 80,
    user_agent: Optional[str] = None,
    prefer_system_chrome: bool = True,
) -> Tuple[Playwright, BrowserContext]:
    """
    Launch a persistent Chrome context with stealth patches, cross-platform.
    """
    username: str = getpass.getuser()
    system: str = platform.system()

    if user_data_dir is None:
        user_data_dir = os.path.join(
            "storage", "browser_profiles", f"chrome_{system.lower()}_{username}")
    user_data_dir = ensure_profile_dir(user_data_dir)

    playwright: Playwright = sync_playwright().start()

    if user_agent is None:
        if system == "Darwin":
            user_agent = (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            )
        else:
            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            )

    common_args: List[str] = [
        "--disable-blink-features=AutomationControlled",
        "--start-maximized",
        "--no-first-run",
        "--no-default-browser-check",
        "--password-store=basic",
    ]

    executable_path: Optional[str] = None
    args: List[str] = list(common_args)

    if system == "Windows" and prefer_system_chrome:
        chrome_path = _find_chrome_executable()
        if chrome_path:
            executable_path = chrome_path
        else:
            print(
                "⚠️ System Chrome not found on Windows; using Playwright Chromium fallback.")

    if system == "Linux":
        args += ["--no-sandbox", "--disable-dev-shm-usage"]

    try:
        context: BrowserContext = playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            executable_path=executable_path,
            headless=headless,
            slow_mo=slow_mo,
            args=args,
            viewport={"width": 1280, "height": 800},
            user_agent=user_agent,
        )

        # Close default blank pages
        for page in context.pages:
            try:
                page.close()
            except Exception:
                pass

        context.add_init_script(STEALTH_JS)
        print(
            f"✅ Launched browser. executable_path={executable_path or 'playwright-chromium'} user_data_dir={user_data_dir}")
        return playwright, context

    except Exception as exc:
        print("⚠️ Browser launch failed with system Chrome:", exc)
        traceback.print_exc()
        try:
            print("ℹ️ Attempting fallback: Playwright bundled Chromium")
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                slow_mo=slow_mo,
                args=args + ["--disable-dev-shm-usage"],
                viewport={"width": 1280, "height": 800},
                user_agent=user_agent,
            )
            for page in context.pages:
                try:
                    page.close()
                except Exception:
                    pass
            context.add_init_script(STEALTH_JS)
            print("✅ Launched Playwright bundled Chromium as fallback.")
            return playwright, context
        except Exception as exc2:
            print("❌ Fallback also failed:", exc2)
            traceback.print_exc()
            try:
                playwright.stop()
            except Exception:
                pass
            raise


def save_session(context: BrowserContext, path: str) -> None:
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    context.storage_state(path=path)


def close_playwright(playwright: Playwright, context: Optional[BrowserContext], show_errors: bool = True) -> None:
    try:
        if context:
            context.close()
            if show_errors:
                print("✅ Browser context closed successfully.")
    except Exception:
        if show_errors:
            print("⚠️ Failed to close browser context!")
            traceback.print_exc()
    try:
        if playwright:
            playwright.stop()
            if show_errors:
                print("✅ Playwright stopped successfully.")
    except Exception:
        if show_errors:
            print("⚠️ Failed to stop Playwright!")
            traceback.print_exc()

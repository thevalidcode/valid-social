from enum import Enum
import os
import typer
from valid_social_cli.utils.stealth_browser import launch_stealth_browser, close_playwright

app = typer.Typer(help="🔐 Login to your social media accounts.")


class PlatformEnum(str, Enum):
    INSTAGRAM = "instagram"
    X = "x"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TIKTOK = "facebook"


@app.callback(invoke_without_command=True)
def login(
    platform: PlatformEnum = typer.Option(
        ...,
        "--platform",
        "-p",
        help="Platform to log into. Options: instagram, x, facebook"
    )
):
    """
     Opens a browser for the user to manually log into the specified platform.
     The session is saved for future automated actions.
     """
    if platform == PlatformEnum.INSTAGRAM:
        profile_path = "storage/browser_profiles/instagram_profile"
        os.makedirs(profile_path, exist_ok=True)

        print("🌐 Launching Instagram login browser...")
        playwright, context = launch_stealth_browser(
            user_data_dir=profile_path,
            headless=False,
            slow_mo=150,
        )

        try:
            page = context.new_page()
            page.goto("https://www.instagram.com/",
                      wait_until="domcontentloaded")

            print("⚠️ Please log in manually in the opened browser window.")
            print(
                "Once logged in and your feed appears, close any popups, then return here.")
            print(
                "⏸️ Waiting for you to finish login (press Resume in Playwright Inspector if needed)...")
            page.pause()

            print(
                "✅ Instagram session saved successfully. You won’t need to log in again.")
        finally:
            close_playwright(playwright, context)

    elif platform == PlatformEnum.X:
        profile_path = "storage/browser_profiles/x_profile"
        os.makedirs(profile_path, exist_ok=True)

        print("🌐 Launching X login browser...")
        playwright, context = launch_stealth_browser(
            user_data_dir=profile_path,
            headless=False,
            slow_mo=150,
        )

        try:
            page = context.new_page()
            page.goto("https://x.com/home",
                      wait_until="domcontentloaded")

            print("⚠️ Please log in manually in the opened browser window.")
            print(
                "Once logged in and your feed appears, close any popups, then return here.")
            print(
                "⏸️ Waiting for you to finish login (press Resume in Playwright Inspector if needed)...")
            page.pause()

            print(
                "✅ X session saved successfully. You won’t need to log in again.")
        finally:
            close_playwright(playwright, context)

    elif platform == PlatformEnum.FACEBOOK:
        profile_path = "storage/browser_profiles/facebook_profile"
        os.makedirs(profile_path, exist_ok=True)

        print("🌐 Launching Facebook login browser...")
        playwright, context = launch_stealth_browser(
            user_data_dir=profile_path,
            headless=False,
            slow_mo=150,
        )

        try:
            page = context.new_page()
            page.goto("https://facebook.com",
                      wait_until="domcontentloaded")

            print("⚠️ Please log in manually in the opened browser window.")
            print(
                "Once logged in and your feed appears, close any popups, then return here.")
            print(
                "⏸️ Waiting for you to finish login (press Resume in Playwright Inspector if needed)...")
            page.pause()

            print(
                "✅ Facebook session saved successfully. You won’t need to log in again.")
        finally:
            close_playwright(playwright, context)

    else:
        print(f"❌ Unsupported platform: {platform}")


def hello():
    print("Hello World!")

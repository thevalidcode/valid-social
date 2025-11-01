import os
import time
import random
from typing import List, Union, Optional
from valid_social_cli.utils.stealth_browser import launch_stealth_browser, close_playwright


def human_delay(min_sec: float = 0.8, max_sec: float = 2.2):
    """Wait a random short time to mimic human behavior."""
    time.sleep(random.uniform(min_sec, max_sec))


def post_to_x(caption: str, media_path: Optional[Union[str, List[str]]] = None) -> None:
    print("Posting to x...")
    profile_path = "storage/browser_profiles/x_profile"

    # Ensure browser profile directory exists
    os.makedirs(profile_path, exist_ok=True)

    # Launch stealth browser using persistent user_data_dir
    playwright, context = launch_stealth_browser(
        user_data_dir=profile_path,
        headless=True,
        slow_mo=150,
    )

    try:
        page = context.new_page()
        page.goto("https://x.com/home", wait_until="domcontentloaded")
        human_delay(5, 8)

        # --- LOGIN CHECK ---
        login_page = page.get_by_label("Sign in to X").get_by_role("group").locator(
            "div").filter(has_text="Sign in to XSign in with").nth(2)
        try:
            if login_page.is_visible():
                print("⚠️ You are not logged in to X.")
                print("➡️ Please run: valid-social login -p x")
                close_playwright(playwright, context)
                return
        except Exception:
            # If the element doesn't exist, it means you're already logged in
            pass

        # --- OPEN NEW POST DIALOG ---
        try:
            post_link = page.get_by_role("link", name="Post")
            if post_link:
                post_link.first.click()
                print("🪶 Opened post dialog.")
            else:
                raise Exception("Post button not found.")
        except Exception:
            print("❌ Could not find 'Post Link' button — UI may have changed.")
            close_playwright(playwright, context)

        human_delay(2, 4)

        # --- TYPE CAPTION ---
        try:
            textarea = page.locator("div[role='textbox']").first
            for char in caption:
                textarea.type(char, delay=random.uniform(40, 120))
            print("✅ Caption entered successfully.")
            human_delay(1, 2)
        except Exception:
            print("⚠️ Could not find caption text area. Skipping caption.")

        # --- UPLOAD MEDIA (OPTIONAL) ---
        if media_path:
            try:
                file_input = page.locator('input[type="file"]').first
                files = [media_path] if isinstance(
                    media_path, str) else media_path
                file_input.set_input_files(files)
                print(f"✅ Uploaded {len(files)} media file(s).")
                human_delay(3, 6)
            except Exception:
                print("❌ Could not find file input — UI may have changed.")
        else:
            print("ℹ️ No media provided. Posting text-only tweet.")

        # --- POST ---
        # try:
        #     share_button = page.locator(
        #         'button[data-testid="tweetButton"]:not([disabled])')
        #     share_button.click()
        #     human_delay(5, 8)
        #     print("✅ Post published to X successfully!")
        # except Exception:
        #     print("❌ Failed to click final 'Post' button. UI may have changed.")

    finally:
        close_playwright(playwright, context)

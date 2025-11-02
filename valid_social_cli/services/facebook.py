import os
import time
import re
import random
from typing import List, Union, Optional
from valid_social_cli.utils.stealth_browser import launch_stealth_browser, close_playwright


def human_delay(min_sec: float = 0.8, max_sec: float = 2.2):
    """Wait a random short time to mimic human behavior."""
    time.sleep(random.uniform(min_sec, max_sec))


FACEBOOK_PROFILE_PATH = "storage/browser_profiles/facebook_profile"


def post_to_facebook(caption: str, media_path: Optional[Union[str, List[str]]] = None) -> None:
    print("Posting to facebook...")

    # Ensure browser profile directory exists
    os.makedirs(FACEBOOK_PROFILE_PATH, exist_ok=True)

    # Launch stealth browser using persistent user_data_dir
    playwright, context = launch_stealth_browser(
        user_data_dir=FACEBOOK_PROFILE_PATH,
        headless=False,
        slow_mo=150,
    )

    try:
        page = context.new_page()
        page.goto("https://web.facebook.com", wait_until="domcontentloaded")
        human_delay(5, 8)

        # --- LOGIN CHECK ---
        login_button = page.locator("div").filter(
            has_text=re.compile(r"^Log in$")).first
        try:
            if login_button.is_visible():
                print("⚠️ You are not logged in to facebook.")
                print("➡️ Please run: valid-social login -p facebook")
                close_playwright(playwright, context, False)
                return
        except Exception:
            # If the element doesn't exist, it means you're already logged in
            pass

        # --- OPEN NEW POST DIALOG ---
        try:
            post_dialog = page.locator(
                "div[role='button']", has_text=re.compile("what's on your mind", re.I))
            if post_dialog:
                post_dialog.first.click()
                print("🪶 Opened post dialog.")
            else:
                raise Exception("Post dialog button not found.")
        except Exception:
            print("❌ Could not find 'What's on your mind' button — UI may have changed.")
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

        # --- Click Next ---
        for _ in range(2):
            try:
                next_btn = page.locator("div").filter(
                    has_text=re.compile(r"^Next$")).nth(1)
                next_btn.click()
                human_delay(2, 4)
            except Exception:
                print("⚠️ Could not click 'Next' — skipping.")
                continue

        # --- POST ---
        try:
            share_button = page.locator('[aria-label="Post"]')
            share_button.click()
            human_delay(5, 8)
            print("✅ Post published to Facebook successfully!")
        except Exception:
            print("❌ Failed to click final 'Post' button. UI may have changed.")

    finally:
        close_playwright(playwright, context)

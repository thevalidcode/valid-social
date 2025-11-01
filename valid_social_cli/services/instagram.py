import os
import time
import random
import re
from typing import List, Union
from valid_social_cli.utils.stealth_browser import launch_stealth_browser, close_playwright


def human_delay(min_sec: float = 0.8, max_sec: float = 2.2):
    """Wait a random short time to mimic human behavior."""
    time.sleep(random.uniform(min_sec, max_sec))


def post_to_instagram(caption: str, image_path: Union[str, List[str]]):
    """
    Posts to Instagram using an existing logged-in session.
    If the user isn't logged in, instructs them to use the CLI login command.
    """
    print("📸 Posting to Instagram...")

    profile_path = "storage/browser_profiles/instagram_profile"
    os.makedirs(profile_path, exist_ok=True)

    playwright, context = launch_stealth_browser(
        user_data_dir=profile_path,
        headless=True,
        slow_mo=150,
    )

    try:
        page = context.new_page()
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        human_delay(5, 8)

        # Check login state
        try:
            login_button = page.locator("div").filter(
                has_text=re.compile(r"^Log in$")).first
            if login_button.is_visible():
                print("⚠️ You are not logged in to Instagram.")
                print("➡️ Please run: valid-social login -p instagram")
                close_playwright(playwright, context)
                return
        except Exception:
            pass  # Already logged in

        # --- Create New Post ---
        try:
            page.get_by_role("link", name="New post Create").click()
            human_delay(2, 4)
        except Exception:
            print("❌ Could not find 'New post' button — UI may have changed.")
            return

        try:
            page.get_by_role("link", name="Post Post").click()
            human_delay(2, 4)
        except Exception:
            print("⚠️ 'Post' link not found. Continuing anyway.")

        # --- Upload Media ---
        try:
            page.get_by_text(
                "Icon to represent media such as images or videosDrag photos and videos"
            ).click()
            human_delay(2, 4)
        except Exception:
            print("⚠️ Could not find upload container. Trying direct upload...")

        try:
            file_input = page.locator('input[type="file"]').first
            file_input.set_input_files(image_path)
            print("✅ Media file(s) selected successfully.")
        except Exception:
            print("❌ Could not find file input field — UI may have changed.")
            return

        human_delay(3, 6)

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

        # --- Write Caption ---
        try:
            textarea = page.get_by_role("textbox", name="Write a caption...")
            for char in caption:
                textarea.type(char, delay=random.uniform(50, 150))
            print("✅ Caption entered successfully.")
            human_delay(1, 2)
        except Exception:
            print("⚠️ Could not find caption field. Skipping caption.")

        # --- Publish ---
        try:
            page.get_by_role("button", name="Share", exact=True).click()
            human_delay(5, 8)
            print("✅ Post published to Instagram successfully!")
        except Exception:
            print("❌ Failed to share post. Please verify UI elements.")

    finally:
        close_playwright(playwright, context)

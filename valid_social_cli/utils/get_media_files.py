from typing import List, Optional
from valid_social_cli.utils.file_selector import select_file


def get_media_files() -> Optional[List[str]]:
    """Ask user if they want to upload media and handle selection."""
    choice = input(
        "📸 Do you want to upload any media? (y/n): ").strip().lower()

    if choice not in ["y", "yes"]:
        print("ℹ️ Skipping media upload.")
        return None

    print("\n📸 Preparing upload...")
    media_files = select_file(
        title="Select media for upload", multiple=True)

    if not media_files:
        print("⚠️ No media selected. Proceeding without uploads.")
        return None

    # Normalize to list
    if isinstance(media_files, str):
        media_files = [media_files]

    print(f"✅ {len(media_files)} file(s) selected for upload.")
    return media_files

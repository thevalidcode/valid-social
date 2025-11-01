from typing import List, Optional
import typer
from valid_social_cli.services.instagram import post_to_instagram
from valid_social_cli.services.x import post_to_x
from valid_social_cli.services.facebook import post_to_facebook
from valid_social_cli.utils.get_media_files import get_media_files

app = typer.Typer(help="🔐 Post to your social media accounts.")


def get_caption() -> str:
    lines: List[str] = []

    while True:
        print("\n📝 Enter your caption below (supports emoji and multi-line).")
        print("Commands:")
        print("  END    → Finish and submit")
        print("  SHOW   → Show current caption")
        print("  EDIT n → Edit line number n (e.g., EDIT 2)")
        print("  DEL n  → Delete line number n (e.g., DEL 3)")
        print("  CLEAR  → Clear entire caption\n")

        while True:
            user_input = input("> ").strip()

            if user_input.upper() == "END":
                caption = "\n".join(lines).strip()
                if caption:
                    return caption
                else:
                    print("❌ Caption cannot be empty. Keep typing.")
            elif user_input.upper() == "SHOW":
                if not lines:
                    print("(No lines yet)")
                else:
                    print("\nCurrent caption:")
                    for i, l in enumerate(lines, start=1):
                        print(f"{i}: {l}")
                    print()
            elif user_input.upper().startswith("EDIT "):
                try:
                    idx = int(user_input.split()[1]) - 1
                    if 0 <= idx < len(lines):
                        new_line = input(f"Edit line {idx+1}: ")
                        lines[idx] = new_line
                    else:
                        print("❌ Invalid line number.")
                except Exception:
                    print("❌ Invalid command format. Use EDIT n")
            elif user_input.upper().startswith("DEL "):
                try:
                    idx = int(user_input.split()[1]) - 1
                    if 0 <= idx < len(lines):
                        lines.pop(idx)
                        print(f"Line {idx+1} deleted.")
                    else:
                        print("❌ Invalid line number.")
                except Exception:
                    print("❌ Invalid command format. Use DEL n")
            elif user_input.upper() == "CLEAR":
                lines.clear()
                print("Caption cleared.")
            else:
                lines.append(user_input)


def select_platforms() -> List[str]:
    available = ["Instagram", "X", "Facebook", "TikTok", "LinkedIn"]
    print("\n📱 Select platforms to post on:")
    for i, name in enumerate(available, start=1):
        print(f" {i}. {name}")

    selected_indices = input(
        "\nEnter numbers separated by commas (e.g., 1,3): "
    ).strip()

    chosen: List[str] = []
    for i in selected_indices.split(","):
        i = i.strip()
        if i.isdigit() and 1 <= int(i) <= len(available):
            chosen.append(available[int(i) - 1])

    if not chosen:
        print("⚠️ No valid platform selected. Exiting.")
        raise typer.Exit()

    print(f"\n✅ Selected: {', '.join(chosen)}")
    return chosen


@app.callback(invoke_without_command=True)
def post(
    platforms: Optional[List[str]] = typer.Option(
        None, "--platform", "-p", help="Platforms to post on (e.g., Instagram, X)"
    ),
    caption: Optional[str] = typer.Option(
        None, "--caption", "-c", help="Caption text"
    ),
    media: Optional[str] = typer.Option(
        None, "--media", "-m", help="Path to media file"
    ),
):
    """
    Post content to multiple social media platforms.
    """
    # Select platforms
    if not platforms:
        platforms = select_platforms()
    else:
        print(f"\n✅ Selected: {', '.join(platforms)}")

    # Get caption
    if not caption:
        caption = get_caption()

    # Get media
    if not media:
        media_path = get_media_files()
    else:
        media_path = media

    # Handle Instagram
    if "Instagram" in platforms:
        if not isinstance(media_path, (str, list)) or not media_path:
            print("⚠️ No media selected for Instagram.")
            choice = input(
                "Do you want to skip Instagram upload? (yes/no): "
            ).strip().lower()

            if choice not in ("yes", "y"):
                print(
                    "❌ Instagram upload canceled. Please select a media file next time.")
                raise typer.Exit()
            else:
                print("✅ Skipping Instagram upload...")
        else:
            post_to_instagram(caption, media_path)

    if "X" in platforms:
        post_to_x(caption, media_path)
    if "Facebook" in platforms:
        post_to_facebook(caption, media_path)
    if "TikTok" in platforms:
        print("🎵 TikTok upload coming soon.")
    if "LinkedIn" in platforms:
        print("🎵 LinkedIn upload coming soon.")

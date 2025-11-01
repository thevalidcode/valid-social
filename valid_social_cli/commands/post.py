from typing import List, Optional
import typer
from valid_social_cli.services.instagram import post_to_instagram
from valid_social_cli.services.x import post_to_x
from valid_social_cli.utils.get_media_files import get_media_files

app = typer.Typer(help="🔐 Post to your social media accounts.")


def get_caption() -> str:
    print("\n📝 Enter caption below (supports emoji and multi-line).")
    print("Type 'END' on a new line when you're done:\n")

    lines: List[str] = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def select_platforms() -> List[str]:
    available = ["Instagram", "X", "Facebook", "TikTok"]
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
        print("📘 Facebook upload coming soon.")
    if "TikTok" in platforms:
        print("🎵 TikTok upload coming soon.")

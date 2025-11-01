import typer
from valid_social_cli.commands.login import app as login_app
from valid_social_cli.commands.post import app as post_app

app = typer.Typer(
    name="Valid Social CLI",
    help="📱 Valid Social CLI - Automate posting to multiple platforms."
)

# Register sub-apps
app.add_typer(login_app, name="login")
app.add_typer(post_app, name="post")


@app.command()
def hello(name: str):
    """Say hello."""
    print(f"Hello {name}!")


if __name__ == "__main__":
    app()

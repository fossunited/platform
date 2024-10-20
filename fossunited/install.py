import click

from fossunited.setup import after_install as setup


def after_install():
    try:
        click.secho("Setting up fossunited...", fg="blue")
        setup()
        click.secho("App installed successfully!", fg="green")
    except Exception as e:
        BUG_REPORT_URL = "https://github.com/fossunited/fossunited/issues/new"
        click.secho("Installation failed for app: fossunited :(", fg="bright_red")
        click.secho(f"Please try reinstalling the app or report the bug at {BUG_REPORT_URL}")
        raise e

import click

from fossunited.setup import after_install as after_setup
from fossunited.setup import before_install as before_setup


def before_install():
    try:
        click.secho("Setting up fossunited...", fg="blue", bold=True)
        before_setup()
    except Exception as e:
        BUG_REPORT_URL = "https://github.com/fossunited/fossunited/issues/new"
        click.secho("Installation failed for app: fossunited :(", fg="bright_red")
        click.secho(f"Please try reinstalling the app or report the bug at {BUG_REPORT_URL}")
        raise e


def after_install():
    try:
        after_setup()
        click.secho("App installed successfully!", fg="green", bold=True)
    except Exception as e:
        BUG_REPORT_URL = "https://github.com/fossunited/fossunited/issues/new"
        click.secho("Installation failed for app: fossunited :(", fg="bright_red")
        click.secho(f"Please try reinstalling the app or report the bug at {BUG_REPORT_URL}")
        raise e

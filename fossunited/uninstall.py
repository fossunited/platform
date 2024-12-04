import click

from fossunited.setup import before_uninstall as uninstall


def before_uninstall():
    try:
        click.secho("Removing customizations made by fossunited app...", color="blue")
        uninstall()
    except Exception as e:
        BUG_REPORT_URL = "https://github.com/fossunited/fossunited/issues/new"
        click.secho("Failed to remove customizations for fossunited app.", fg="bright_red")
        click.secho(f"Please try again or raise an issue at {BUG_REPORT_URL}")
        raise e

    click.secho("fossunited(app) customizations have been removed successfully!", fg="green")

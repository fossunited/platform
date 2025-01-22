import click
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from fossunited.setup import create_custom_roles, get_custom_fields, get_custom_roles


def before_migrate():
    try:
        handle_custom_fields()
        handle_custom_roles()
    except Exception as e:
        BUG_REPORT_URL = "https://github.com/fossunited/fossunited/issues/new"
        click.secho("Before migration failed for app: fossunited :(", fg="bright_red")
        click.secho(f"Please try reinstalling the app or report the bug at {BUG_REPORT_URL}")
        raise e


def handle_custom_fields():
    """
    Get all the required custom fields and add them to the app
    """
    missing_custom_fields = has_custom_fields()
    if not missing_custom_fields:
        click.secho("All custom fields are already added.", fg="blue", bold=True)
        return

    # Add missing custom fields
    click.secho("Adding custom fields...", fg="cyan")
    create_custom_fields(missing_custom_fields, ignore_validate=True)
    click.secho("Custom fields added!", fg="green", bold=True)


def has_custom_fields():
    """
    Check which custom fields from get_custom_fields() are not yet in the database.

    :return: A dictionary of doctype:fields that are missing from the database
    """
    custom_fields = get_custom_fields()
    missing_fields = {}

    for doctype, fields in custom_fields.items():
        # Check each field for this doctype
        doctype_missing_fields = []
        for field in fields:
            # Check if the field already exists in the database
            exists = frappe.db.exists(
                "Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}
            )

            if not exists:
                doctype_missing_fields.append(field)

        # If there are missing fields for this doctype, add to the result
        if doctype_missing_fields:
            missing_fields[doctype] = doctype_missing_fields

    return missing_fields


def handle_custom_roles():
    """
    Get all the required roles and add them to the app
    """
    roles = get_custom_roles()

    click.secho("Adding custom roles...", fg="cyan")
    create_custom_roles(roles)
    click.secho("Custom roles added!", fg="green", bold=True)

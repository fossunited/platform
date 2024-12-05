import click
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from fossunited.setup import get_custom_fields


def after_migrate():
    try:
        missing_custom_fields = has_custom_fields()
        if not missing_custom_fields:
            click.secho("All custom fields are already added.", fg="blue")
            return

        # Add missing custom fields
        click.secho("Adding custom fields...", fg="blue")
        create_custom_fields(missing_custom_fields, ignore_validate=True)
        click.secho("Custom fields added!", fg="green")
    except Exception as e:
        BUG_REPORT_URL = "https://github.com/fossunited/fossunited/issues/new"
        click.secho("After migration failed for app: fossunited :(", fg="bright_red")
        click.secho(f"Please try reinstalling the app or report the bug at {BUG_REPORT_URL}")
        raise e


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

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    create_custom_fields(get_custom_fields(), ignore_validate=True)


def before_uninstall():
    delete_custom_fields(get_custom_fields())


def delete_custom_fields(custom_fields: dict):
    """
    :param custom_fields: a dict like `{'Salary Slip': [{fieldname: 'loans', ...}]}`
    """
    for doctype, fields in custom_fields.items():
        frappe.db.delete(
            "Custom Field",
            {
                "fieldname": ("in", [field["fieldname"] for field in fields]),
                "dt": doctype,
            },
        )

        frappe.clear_cache(doctype=doctype)


def get_custom_fields():
    """
    FOSSUnited specific custom fields that need to be added to base Frappe doctypes
    """

    return {
        "Email Template": [
            {
                "fieldname": "linked_chapter_section",
                "fieldtype": "Section Break",
                "label": "Linked Chapter Details",
                "insert_after": "response",
            },
            {
                "fieldname": "chapter",
                "fieldtype": "Link",
                "label": "Chapter",
                "options": "FOSS Chapter",
                "insert_after": "linked_chapter_section",
            },
            {
                "fieldname": "event",
                "fieldtype": "Link",
                "label": "Event",
                "options": "FOSS Chapter Event",
                "insert_after": "chapter",
            },
        ],
        "Email Group": [
            {
                "fieldname": "linked_chapter_section",
                "fieldtype": "Section Break",
                "label": "Linked Chapter Details",
                "insert_after": "total_subscribers",
            },
            {
                "fieldname": "chapter",
                "fieldtype": "Link",
                "label": "Chapter",
                "options": "FOSS Chapter",
                "insert_after": "linked_chapter_section",
            },
            {
                "fieldname": "event",
                "fieldtype": "Link",
                "label": "Event",
                "options": "FOSS Chapter Event",
                "insert_after": "chapter",
            },
        ],
    }

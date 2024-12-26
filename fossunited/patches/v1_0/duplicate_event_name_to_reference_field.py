import frappe


def execute():
    """
    In this patch, we will be going through every existing Email Groups, Email Templates,
    and Newsletters & we will be copying the value of the `event` field to the
    `reference_document` field of the same document.
    """
    email_templates = frappe.get_all(
        "Email Template",
        filters={"event": ("!=", "")},
        fields=["name", "event"],
    )
    for email_template in email_templates:
        frappe.db.set_value(
            "Email Template",
            email_template.name,
            "reference_document",
            email_template.event,
        )

    email_groups = frappe.get_all(
        "Email Group",
        filters={"chapter": ("!=", "")},
        fields=["name", "event"],
    )
    for email_group in email_groups:
        frappe.db.set_value(
            "Email Group", email_group.name, "reference_document", email_group.event
        )

    newsletters = frappe.get_all(
        "Newsletter",
        filters={"event": ("!=", "")},
        fields=["name", "event"],
    )
    for newsletter in newsletters:
        frappe.db.set_value("Newsletter", newsletter.name, "reference_document", newsletter.event)

from typing import Literal

import frappe

from fossunited.doctype_ids import EVENT

EMAIL_GROUP_TYPES = Literal[
    "Chapter Master",
    "Event Participants",
    "CFP Proposers",
    "Accepted Proposers",
    "Rejected Proposers",
    "Other",
]


def create_email_group(
    event_id: str,
    type: EMAIL_GROUP_TYPES,
):
    """
    Create an email group linked to the event

    Args:
        event: event id
        session_user: session user id
    """
    _event = frappe.get_doc(EVENT, event_id)

    # if not check_if_chapter_member(_event.chapter, session_user):
    #     raise frappe.PermissionError("You are not authorised for this action.")

    if frappe.db.exists(
        "Email Group", {"event": event_id, "chapter": _event.chapter, "group_type": type}
    ):
        raise frappe.ValidationError("Email Group already exists for this event")

    group_title = f"{type}-{_event.event_name}-{_event.chapter_name}-{event_id}"
    _group_title = group_title[:140]
    group = frappe.get_doc(
        {
            "doctype": "Email Group",
            "title": _group_title,
            "chapter": _event.chapter,
            "event": event_id,
            "group_type": type,
        }
    )

    try:
        group.insert(ignore_permissions=True)
    except Exception as e:
        frappe.throw(f"Error while creating email group: {e}", frappe.ValidationError)

    group.reload()
    return group


def add_to_email_group(email_group: str, email: str):
    """
    Add an email to an email group

    Args:
        email_group: id of email group
        email: email to be added to the group
    """

    if not frappe.db.exists("Email Group", email_group):
        frappe.throw("This email group does not exist", frappe.DoesNotExistError)

    if frappe.db.exists("Email Group Member", {"email_group": email_group, "email": email}):
        frappe.throw("Email already a part of this email group", frappe.ValidationError)

    member = frappe.get_doc(
        {"doctype": "Email Group Member", "email_group": email_group, "email": email}
    )
    member.insert(ignore_permissions=True)

import frappe
from frappe.model.document import Document

from fossunited.api.emailing import add_to_email_group, create_email_group
from fossunited.doctype_ids import EVENT_RSVP, RSVP_RESPONSE


class FOSSEventRSVPSubmission(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.foss_custom_answer.foss_custom_answer import (
            FOSSCustomAnswer,
        )

        chapter: DF.Data | None
        confirm_attendance: DF.Check
        custom_answers: DF.Table[FOSSCustomAnswer]
        email: DF.Data
        event: DF.Data
        event_name: DF.Data | None
        im_a: DF.Literal["", "Student", "Professional", "FOSS Enthusiast", "Other"]  # noqa: F722, F821
        linked_rsvp: DF.Link
        name1: DF.Data
        submitted_by: DF.Link | None
    # end: auto-generated types

    pass

    def validate(self):
        self.validate_linked_rsvp_exists()

    def after_insert(self):
        self.close_rsvp_on_max_count()
        self.handle_add_to_email_group()

    def close_rsvp_on_max_count(self):
        max_count = self.get_max_count()
        submission_count = frappe.db.count(
            RSVP_RESPONSE,
            {"linked_rsvp": self.linked_rsvp},
        )

        if submission_count >= max_count:
            frappe.db.set_value(
                EVENT_RSVP,
                self.linked_rsvp,
                "is_published",
                False,
            )

    def get_max_count(self):
        max_count = frappe.db.get_value(EVENT_RSVP, self.linked_rsvp, "max_rsvp_count")
        return max_count

    def validate_linked_rsvp_exists(self):
        if not frappe.db.exists(EVENT_RSVP, self.linked_rsvp):
            frappe.throw("Invalid RSVP", frappe.DoesNotExistError)

        is_rsvp_published = frappe.db.get_value(EVENT_RSVP, self.linked_rsvp, "is_published")
        if not is_rsvp_published:
            frappe.throw("RSVP is not published", frappe.PermissionError)

    def handle_add_to_email_group(self):
        if not frappe.db.exists(
            "Email Group", {"event": self.event, "group_type": "Event Participants"}
        ):
            create_email_group(self.event, "Event Participants")

        email_group = frappe.db.get_value(
            "Email Group", {"event": self.event, "group_type": "Event Participants"}, ["name"]
        )
        add_to_email_group(email_group, self.email)

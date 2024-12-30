# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.api.emailing import add_to_email_group, create_email_group
from fossunited.doctype_ids import EMAIL_GROUP, HACKATHON, HACKATHON_LOCALHOST


class FOSSHackathonParticipant(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        email: DF.Data
        full_name: DF.Data
        git_profile: DF.Data | None
        hackathon: DF.Link
        is_student: DF.Check
        localhost: DF.Link | None
        localhost_request_status: DF.Literal[
            "Pending", "Pending Confirmation", "Accepted", "Rejected"  # noqa: F722, F821
        ]
        organization: DF.Data | None
        user: DF.Link | None
        user_profile: DF.Link | None
        wants_to_attend_locally: DF.Check
    # end: auto-generated types

    def after_insert(self):
        self.add_to_email_group()

    def before_save(self):
        if self.has_value_changed("wants_to_attend_locally"):
            self.handle_localhost_request()
        self.handle_localhost_rejection()
        if self.has_value_changed("localhost"):
            self.update_request_status()

    def validate(self):
        if self.wants_to_attend_locally and not self.localhost:
            frappe.throw("No LocalHost value provided", frappe.ValidationError)

    def add_to_email_group(self):
        if not frappe.db.exists(
            EMAIL_GROUP,
            {
                "document_type": HACKATHON,
                "reference_document": self.hackathon,
                "group_type": "Event Participants",
            },
        ):
            create_email_group(
                type="Event Participants",
                reference_document=self.hackathon,
                document_type=HACKATHON,
            )

        email_group = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.hackathon,
                "document_type": HACKATHON,
                "group_type": "Event Participants",
            },
            ["name"],
        )

        add_to_email_group(email_group, self.email)

    def update_request_status(self):
        self.localhost_request_status = "Pending"

    def handle_localhost_rejection(self):
        if not self.has_value_changed("localhost") and self.localhost_request_status == "Rejected":
            localhost_name = frappe.db.get_value(
                HACKATHON_LOCALHOST, self.localhost, "localhost_name"
            )
            self.add_comment(
                "Comment",
                f"Rejected by localhost: {localhost_name}",
            )
            self.wants_to_attend_locally = False

    def handle_localhost_request(self):
        prev_doc = self.get_doc_before_save()
        if not prev_doc:
            return

        if frappe.db.get_value("User", frappe.session.user, "user_type") == "System User":
            return

        if not self.wants_to_attend_locally:
            return

        if (self.localhost == prev_doc.localhost) and self.localhost_request_status == "Rejected":
            frappe.throw(
                "You have already been rejected from this localhost.", frappe.PermissionError
            )

        self.localhost_request_status = "Pending"

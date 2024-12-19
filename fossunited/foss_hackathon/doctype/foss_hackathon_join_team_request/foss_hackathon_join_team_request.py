# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
import frappe.permissions
from frappe.model.document import Document

from fossunited.doctype_ids import (
    HACKATHON_PARTICIPANT,
    HACKATHON_TEAM,
    HACKATHON_TEAM_MEMBER,
    JOIN_TEAM_REQUEST,
)


class FOSSHackathonJoinTeamRequest(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        hackathon: DF.Link
        hackathon_name: DF.Data | None
        is_outgoing_request: DF.Check
        reciever_email: DF.Data
        requested_by: DF.Link
        sender_name: DF.Data | None
        status: DF.Literal["Pending", "Accepted", "Rejected"]  # noqa: F821
        team: DF.Link
        team_name: DF.Data | None
    # end: auto-generated types

    def before_insert(self):
        self.validate_sender_as_member()

    def before_save(self):
        if self.has_value_changed("status"):
            if self.status == "Accepted":
                self.add_member_to_team()
                self.reject_other_requests()

    def add_member_to_team(self):
        # get participant doc
        try:
            participant_doc = frappe.get_doc(
                HACKATHON_PARTICIPANT,
                {
                    "email": self.reciever_email,
                    "hackathon": self.hackathon,
                },
            )
        except frappe.DoesNotExistError:
            frappe.throw("Participant not found")
            return

        team_doc = frappe.get_doc(HACKATHON_TEAM, self.team)
        team_doc.append("members", {"member": participant_doc.name})
        team_doc.save()

    def reject_other_requests(self):
        requests = frappe.get_all(
            JOIN_TEAM_REQUEST,
            filters={
                "hackathon": self.hackathon,
                "status": "Pending",
                "reciever_email": self.reciever_email,
                "name": ["!=", self.name],
            },
            pluck="name",
        )
        for request in requests:
            request_doc = frappe.get_doc(JOIN_TEAM_REQUEST, request)
            request_doc.status = "Rejected"
            request_doc.save(ignore_permissions=True)

    def validate_sender_as_member(self):
        """
        Validate that the user sending the invite (session user) is either a member
        of the team or a has System User role.

        System users should be able to make changes to this doctype for support reasons.
        """
        if frappe.permissions.is_system_user(frappe.session.user):
            return

        participant_id = frappe.db.get_value(
            HACKATHON_PARTICIPANT, {"user": self.requested_by}, ["name"]
        )

        is_team_member = frappe.db.exists(
            HACKATHON_TEAM_MEMBER, {"parent": self.team, "member": participant_id}
        )

        if not is_team_member:
            frappe.throw("Request sender is not a team member", frappe.ValidationError)

        return

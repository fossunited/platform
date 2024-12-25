# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import (
    HACKATHON_LOCALHOST,
    LOCALHOST_ORGANIZER,
    USER_PROFILE,
)


class FOSSHackathonLocalHost(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_hackathon.doctype.foss_hackathon_localhost_organizer.foss_hackathon_localhost_organizer import (  # noqa: E501
            FOSSHackathonLocalHostOrganizer,
        )

        city: DF.Link | None
        is_accepting_attendees: DF.Check
        localhost_name: DF.Data
        location: DF.Data | None
        map_link: DF.Data | None
        organizers: DF.Table[FOSSHackathonLocalHostOrganizer]
        parent_hackathon: DF.Link
        state: DF.Link | None
    # end: auto-generated types
    pass

    def before_insert(self):
        members = [member.profile for member in self.organizers]
        self.assign_localhost_organizer_role(members)

    def on_trash(self):
        members = [member.profile for member in self.organizers]
        self.remove_organizer_role(members)

    def before_save(self):
        self.handle_roles()

    def handle_roles(self):
        if self.is_new():
            return

        organizers = self.get("organizers")
        organizers_old = self.get_doc_before_save().get("organizers")

        # get members that are in curr member but not in old members
        new_members = [
            member.profile
            for member in organizers
            if member.profile not in [m.profile for m in organizers_old]
        ]
        removed_members = [
            member.profile
            for member in organizers_old
            if member.profile not in [m.profile for m in organizers]
        ]

        self.assign_localhost_organizer_role(new_members)
        self.remove_organizer_role(removed_members)

    def assign_localhost_organizer_role(self, members: list):
        for member in members:
            user = frappe.get_doc(
                "User",
                frappe.db.get_value(USER_PROFILE, member, "user"),
            )
            user.add_roles("Localhost Organizer")
            user.save(ignore_permissions=True)

    def remove_organizer_role(self, members: list):
        for member in members:
            if self.is_other_localhost_member(member):
                continue
            user = frappe.get_doc(
                "User",
                frappe.db.get_value(USER_PROFILE, member, "user"),
            )
            user.remove_roles("Localhost Organizer")
            user.save(ignore_permissions=True)

    def is_other_localhost_member(self, member: str) -> bool:
        """
        Check if the member is part of any other localhost
        """
        is_member = frappe.db.exists(
            HACKATHON_LOCALHOST,
            [
                [
                    LOCALHOST_ORGANIZER,
                    "profile",
                    "=",
                    member,
                ],
                ["name", "!=", self.name],
            ],
        )
        return bool(is_member)

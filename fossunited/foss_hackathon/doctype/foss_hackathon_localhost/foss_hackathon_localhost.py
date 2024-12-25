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
        member_profiles = [member.profile for member in self.organizers]
        self.assign_localhost_organizer_role(member_profiles)

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

        new_profiles = {member.profile for member in organizers}
        old_profiles = {member.profile for member in organizers_old}

        # using sets makes the comparisons faster
        profiles_to_add = list(new_profiles - old_profiles)
        profiles_to_remove = list(old_profiles - new_profiles)

        self.assign_localhost_organizer_role(profiles_to_add)
        self.remove_organizer_role(profiles_to_remove)

    def assign_localhost_organizer_role(self, profiles: list):
        for profile in profiles:
            user = frappe.get_doc(
                "User",
                frappe.db.get_value(USER_PROFILE, profile, "user"),
            )
            user.add_roles("Localhost Organizer")
            user.save(ignore_permissions=True)

    def remove_organizer_role(self, profiles: list):
        for profile in profiles:
            if self.is_other_localhost_member(profile):
                continue
            user = frappe.get_doc(
                "User",
                frappe.db.get_value(USER_PROFILE, profile, "user"),
            )
            user.remove_roles("Localhost Organizer")
            user.save(ignore_permissions=True)

    def is_other_localhost_member(self, profile: str) -> bool:
        """
        Check if the profile is an organizer of another localhost
        """
        is_member = frappe.db.exists(
            HACKATHON_LOCALHOST,
            [
                [
                    LOCALHOST_ORGANIZER,
                    "profile",
                    "=",
                    profile,
                ],
                ["name", "!=", self.name],
            ],
        )
        return bool(is_member)

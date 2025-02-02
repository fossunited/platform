# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.doctype_ids import (
    HACKATHON,
    HACKATHON_LOCALHOST,
    HACKATHON_PARTICIPANT,
    LOCALHOST_ORGANIZER,
    USER_PROFILE,
)


class FOSSHackathonLocalHost(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_hackathon.doctype.foss_hackathon_localhost_organizer.foss_hackathon_localhost_organizer import (  # noqa: E501
            FOSSHackathonLocalHostOrganizer,
        )

        city: DF.Link | None
        email: DF.Data | None
        image: DF.AttachImage | None
        is_accepting_attendees: DF.Check
        is_published: DF.Check
        localhost_name: DF.Data
        location: DF.Data | None
        map_link: DF.Data | None
        organizers: DF.Table[FOSSHackathonLocalHostOrganizer]
        parent_hackathon: DF.Link
        route: DF.Data | None
        slug: DF.Data | None
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
        self.set_route()
        self.handle_roles()

    def get_context(self, context):
        context.no_cache = 1
        context.breadcrumbs = self.get_breadcrumb()
        context.hackathon = frappe.db.get_value(
            HACKATHON,
            self.parent_hackathon,
            [
                "hackathon_name",
                "route",
                "hackathon_logo",
                "hackathon_rules",
                "hackathon_faq",
                "start_date",
                "end_date",
                "hackathon_description",
            ],
            as_dict=True,
        )
        context.hackathon_format_date = self.get_formatted_date(context.hackathon)
        context.registration_link = f"/dashboard/register-for-hackathon?id={self.parent_hackathon}"
        context.attending = self.get_attending_stat()
        context.interested = self.get_interested_stat()
        context.organizers = self.get_organizers()
        context.has_liked = frappe.session.user in self.get_liked_by()

    def set_route(self):
        hackathon_route = frappe.db.get_value(HACKATHON, self.parent_hackathon, "route")
        if not self.slug:
            self.slug = frappe.scrub(self.localhost_name)
        self.route = f"{hackathon_route}/host/{self.slug}"

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

    def get_breadcrumb(self):
        crumbs = [
            {
                "route": f'/{frappe.db.get_value(HACKATHON, self.parent_hackathon, "route")}',
                "label": frappe.db.get_value(HACKATHON, self.parent_hackathon, "hackathon_name"),
            },
            {
                "label": "localhost",
            },
            {
                "label": self.localhost_name,
            },
        ]

        return crumbs

    def get_attending_stat(self):
        attending_count = frappe.db.count(
            HACKATHON_PARTICIPANT, {"localhost": self.name, "localhost_request_status": "Accepted"}
        )

        return attending_count

    def get_interested_stat(self):
        pending_participants = frappe.db.count(
            HACKATHON_PARTICIPANT, {"localhost": self.name, "localhost_request_status": "Pending"}
        )
        localhost_likes = frappe.db.count(
            "Comment",
            {
                "comment_type": "Like",
                "reference_doctype": HACKATHON_LOCALHOST,
                "reference_name": self.name,
            },
        )

        return int(pending_participants + localhost_likes)

    def get_formatted_date(self, hackathon):
        start_date = hackathon.start_date
        end_date = hackathon.end_date

        if start_date.year != end_date.year:
            # Format: 30 Dec 2024 - 2 Jan 2025
            return f"{start_date.day} {start_date.strftime('%b')} {start_date.year} - {end_date.day} {end_date.strftime('%b')} {end_date.year}"  # noqa: E501

        if start_date.month != end_date.month:
            # Format: 31 Jan - 2 Feb 2025
            return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')} {start_date.year}"  # noqa: E501

        # Format: 2-3 Feb 2025
        return f"{start_date.day} - {end_date.day} {start_date.strftime('%b')} {start_date.year}"

    def get_organizers(self):
        organizers = []

        for member in self.organizers:
            organizer = frappe.db.get_value(
                USER_PROFILE,
                {"name": member.profile},
                ["route", "full_name", "profile_photo"],
                as_dict=True,
            )
            organizers.append(organizer)

        return organizers

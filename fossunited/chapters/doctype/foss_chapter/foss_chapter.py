# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.doctype_ids import EVENT, STUDENT_CLUB, USER_PROFILE


class FOSSChapter(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.chapters.doctype.foss_chapter_lead_team_member.foss_chapter_lead_team_member import (  # noqa: E501
            FOSSChapterLeadTeamMember,
        )

        about_chapter: DF.TextEditor | None
        banner_image: DF.AttachImage | None
        chapter_lead: DF.Link | None
        chapter_members: DF.Table[FOSSChapterLeadTeamMember]
        chapter_name: DF.Data
        chapter_type: DF.Literal["City Community", "FOSS Club", "Conference"]  # noqa: F722, F821
        city: DF.Link | None
        country: DF.Link | None
        discord: DF.Data | None
        email: DF.Data
        facebook: DF.Data | None
        google_map_link: DF.Data | None
        instagram: DF.Data | None
        institution_name: DF.Link | None
        is_published: DF.Check
        linkedin: DF.Data | None
        mastodon: DF.Data | None
        matrix: DF.Data | None
        represent_image: DF.AttachImage | None
        route: DF.Data | None
        slug: DF.Data | None
        state: DF.Link | None
        telegram: DF.Data | None
        whatsapp: DF.Data | None
        x: DF.Data | None
    # end: auto-generated types

    def before_insert(self):
        self.handle_member_addition()

    def validate(self):
        self.make_city_name_upper()
        self.validate_slug()

    def before_save(self):
        self.set_chapter_lead()
        self.set_route()

    def on_update(self):
        self.handle_member_addition()
        self.handle_member_removal()

    def handle_member_addition(self):
        # for each member, add roles of 'Chapter Team Member'
        for member in self.chapter_members:
            user = frappe.db.get_value(USER_PROFILE, member.chapter_member, "user")

            if frappe.db.exists(
                "Has Role",
                {"role": "Chapter Team Member", "parent": user},
            ):
                continue

            roles = ["Chapter Team Member"]
            if member.role == "Lead":
                roles.append("Chapter Lead")

            self.add_member_roles(user, *roles)

    def handle_member_removal(self):
        prev_doc = self.get_doc_before_save()
        if not prev_doc:
            return
        for member in prev_doc.chapter_members:
            if member.chapter_member not in [d.chapter_member for d in self.chapter_members]:
                if self.member_of_other_chapter(member):
                    continue
                user = frappe.db.get_value(USER_PROFILE, member.chapter_member, "user")

                roles = ["Chapter Team Member"]
                if member.role == "Lead":
                    roles.append("Chapter Lead")

                self.remove_member_roles(user, *roles)

    def add_member_roles(self, user, *roles):
        user = frappe.get_doc("User", user)
        existing_roles = {d.role: d for d in user.get("roles")}
        for role in roles:
            if role not in existing_roles:
                user.append("roles", {"role": role})
        user.save(ignore_permissions=True)

    def remove_member_roles(self, user, *roles):
        user = frappe.get_doc("User", user)
        existing_roles = {d.role: d for d in user.get("roles")}

        for role in roles:
            if role in existing_roles:
                user.get("roles").remove(existing_roles[role])
        user.save(ignore_permissions=True)

    def member_of_other_chapter(self, member):
        return bool(
            frappe.db.exists(
                "FOSS Chapter Lead Team Member",
                {
                    "chapter_member": member.chapter_member,
                    "parent": ["!=", self.name],
                },
            )
        )

    def set_chapter_lead(self):
        for member in self.chapter_members:
            if member.role == "Lead":
                self.chapter_lead = member.chapter_member
                break

    def set_route(self):
        if not self.slug:
            self.set_slug()

        if self.route and not self.has_value_changed("slug"):
            return

        self.route = f"c/{self.slug}"

    def set_slug(self):
        if not self.slug:
            self.slug = frappe.scrub(self.chapter_name).replace("_", "-")

    def validate_slug(self):
        if not self.slug:
            self.set_slug()

        if frappe.db.exists("FOSS Chapter", {"slug": self.slug, "name": ["!=", self.name]}):
            frappe.throw(
                f"Chapter with slug {self.slug} already exists", frappe.UniqueValidationError
            )

        if " " in self.slug:
            frappe.throw("Slug cannot have spaces")

    def get_context(self, context):
        if self.chapter_type == "City Community":
            context.profile_img_src = "/assets/fossunited/images/chapter/city_profile.svg"
            context.default_banner = "/assets/fossunited/images/chapter/city_community_banner.png"
        elif self.chapter_type == STUDENT_CLUB:
            context.profile_img_src = "/assets/fossunited/images/chapter/foss_club_profile.svg"
            context.default_banner = "/assets/fossunited/images/chapter/foss_club_banner.png"
        else:
            context.profile_img_src = None

        context.upcoming_events = self.get_upcoming_events()
        context.past_events = self.get_past_events()
        context.members = self.get_members()
        context.social_links = self.get_social_links()

    # make the chapter name upper case if it is a city community
    def make_city_name_upper(self):
        if self.chapter_type == "City Community":
            self.chapter_name = self.city.upper()

    def get_upcoming_events(self):
        return frappe.get_all(
            EVENT,
            filters={
                "chapter": self.name,
                "event_end_date": (">=", frappe.utils.now()),
                "status": ["in", ["Approved", "Live"]],
            },
            fields=[
                "name",
                "route",
                "chapter",
                "event_start_date",
                "event_name",
                "banner_image",
                "must_attend",
                "event_location",
            ],
            order_by="event_start_date asc",
            page_length=6,
        )

    def get_past_events(self):
        return frappe.get_all(
            EVENT,
            filters={
                "chapter": self.name,
                "event_end_date": ("<", frappe.utils.now()),
                "status": "Concluded",
            },
            fields=[
                "name",
                "route",
                "chapter",
                "event_start_date",
                "event_name",
                "banner_image",
                "must_attend",
                "event_location",
            ],
            order_by="event_end_date desc",
            page_length=999,
        )

    def get_members(self):
        members = []
        for member in self.chapter_members:
            profile = frappe.get_doc(USER_PROFILE, member.chapter_member).as_dict()
            members.append(
                {
                    "full_name": member.full_name,
                    "role": member.role,
                    "profile_picture": (
                        profile.profile_photo
                        if profile.profile_photo
                        else "/assets/fossunited/images/defaults/user_profile_image.png"
                    ),
                    "route": profile.route,
                }
            )
        return members

    def get_social_links(self):
        socials = {}
        SOCIAL_LINK_FIELDNAMES = [
            "github",
            "gitlab",
            "x",
            "linkedin",
            "instagram",
            "mastodon",
            "youtube",
            "medium",
            "facebook",
            "matrix",
            "telegram",
            "whatsapp",
            "discord",
        ]
        for k, v in self.as_dict().items():
            if k in SOCIAL_LINK_FIELDNAMES:
                if v:
                    socials[k] = v
            else:
                continue

        return socials

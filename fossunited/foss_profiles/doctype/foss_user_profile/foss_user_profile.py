# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import re

import frappe
from frappe.exceptions import PermissionError
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.profile import is_valid_username


class PrivateProfileError(PermissionError):
    """Exception raised when trying to access a private profile."""

    pass


class FOSSUserProfile(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.foss_profiles.doctype.foss_user_profile_education.foss_user_profile_education import (  # noqa: E501
            FOSSUserProfileEducation,
        )
        from fossunited.foss_profiles.doctype.foss_user_profile_work_experience.foss_user_profile_work_experience import (  # noqa: E501
            FOSSUserProfileWorkExperience,
        )
        from fossunited.foss_profiles.doctype.foss_user_projects.foss_user_projects import (
            FOSSUserProjects,
        )
        from fossunited.foss_profiles.doctype.foss_user_skill_multiselect.foss_user_skill_multiselect import (  # noqa: E501
            FOSSUserSkillMultiselect,
        )

        about: DF.TextEditor | None
        bio: DF.SmallText | None
        cover_image: DF.AttachImage | None
        current_city: DF.Link | None
        devto: DF.Data | None
        education: DF.Table[FOSSUserProfileEducation]
        email: DF.Data | None
        experience: DF.Table[FOSSUserProfileWorkExperience]
        full_name: DF.Data | None
        gender: DF.Data | None
        github: DF.Data | None
        gitlab: DF.Data | None
        instagram: DF.Data | None
        is_private: DF.Check
        is_published: DF.Check
        linkedin: DF.Data | None
        mastodon: DF.Data | None
        medium: DF.Data | None
        profile_photo: DF.AttachImage | None
        projects: DF.Table[FOSSUserProjects]
        route: DF.Data | None
        skills: DF.TableMultiSelect[FOSSUserSkillMultiselect]
        user: DF.Link
        username: DF.Data
        website: DF.Data | None
        x: DF.Data | None
        youtube: DF.Data | None
    # end: auto-generated types

    def validate(self):
        self.validate_username()
        self.set_route()

    def on_update(self):
        prev_user_doc = self.get_doc_before_save()
        if prev_user_doc is None:
            return
        try:
            if self.full_name is not self.get_doc_before_save().full_name:
                frappe.db.set_value(
                    "User",
                    {"email": self.email},
                    "full_name",
                    self.full_name,
                )
            if self.username is not self.get_doc_before_save().username:
                frappe.db.set_value(
                    "User",
                    {"email": self.email},
                    "username",
                    self.username,
                )
        except Exception as e:
            frappe.log_error(f"Error updating user details: {str(e)}")
            frappe.throw("Error updating user details")

    def validate_username(self):
        if not (3 <= len(self.username) <= 30):
            frappe.throw("Username must be between 3 and 30 characters")

        if not re.match(r"^[a-z0-9_\.]+$", self.username):
            frappe.throw(
                "Username can only contain lowercase letters, numbers, underscores and dots."
            )

        if re.search(
            r"\.(txt|html|php|js|json|xml|css|htm)$",
            self.username,
            re.IGNORECASE,
        ):
            frappe.throw("Username cannot end with extensions like .txt, .html, etc.")

        if not is_valid_username(self.username, self.name):
            frappe.throw("Username is already taken or restricted.")

    def set_route(self):
        self.route = f"u/{self.username}"

    def get_context(self, context):
        if self.is_private and frappe.session.user not in (
            "Administrator",
            self.user,
        ):
            frappe.throw("Profile is Private", PrivateProfileError)

        experiences_dict = {}
        for experience in self.experience:
            if experience.company not in experiences_dict:
                experiences_dict[experience.company] = []
            experiences_dict[experience.company].append(experience.as_dict())
        context.experiences_dict = experiences_dict
        context.no_cache = 1

    def on_trash(self):
        frappe.delete_doc("User", self.user, force=True)

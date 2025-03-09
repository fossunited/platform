# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import USER_PROFILE


class GlobalCFPSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.foss_global_cfp_review_member.foss_global_cfp_review_member import (  # noqa: E501
            FOSSGlobalCFPReviewMember,
        )

        guidelines: DF.TextEditor | None
        members: DF.Table[FOSSGlobalCFPReviewMember]
    # end: auto-generated types

    def before_save(self):
        # unassign 'CFP Reviewer role to all the members removed
        self.unassign_reviewer_role()
        # assign 'CFP Reviewer' role to all members
        self.assign_reviewer_role()

    def assign_reviewer_role(self):
        for member in self.members:
            user = frappe.get_doc(
                "User",
                frappe.db.get_value(USER_PROFILE, member.profile, "user"),
            )
            user.add_roles("CFP Reviewer")

    def unassign_reviewer_role(self):
        if self.is_new():
            return
        past_members = self.get_doc_before_save().members

        for member in past_members:
            if member not in self.members:
                user = frappe.get_doc(
                    "User",
                    frappe.db.get_value(
                        USER_PROFILE,
                        member.profile,
                        "user",
                    ),
                )
                user.remove_roles("CFP Reviewer")

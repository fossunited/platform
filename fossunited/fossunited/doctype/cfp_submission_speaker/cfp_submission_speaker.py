# Copyright (c) 2025, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CFPSubmissionSpeaker(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        bio: DF.TextEditor | None
        designation: DF.Data
        email: DF.Data
        full_name: DF.Data
        linked_user: DF.Link | None
        organization: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        photo: DF.AttachImage | None
        social_link: DF.Data | None
    # end: auto-generated types

    pass

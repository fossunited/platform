# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
from frappe.model.document import Document


class FOSSEventCommunityPartner(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        link: DF.Data
        logo: DF.AttachImage
        org_name: DF.Data
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
    # end: auto-generated types

    pass

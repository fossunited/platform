# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class FOSSEventSponsor(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        custom_tier: DF.Data | None
        image: DF.AttachImage | None
        link: DF.Data
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        sponsor_name: DF.Data
        tier: DF.Literal["Platinum", "Gold", "Silver", "Bronze", "Venue Partner", "Custom"]  # noqa: F722, F821
    # end: auto-generated types

    pass

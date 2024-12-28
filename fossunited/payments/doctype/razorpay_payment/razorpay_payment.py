# Copyright (c) 2024, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fossunited.doctype_ids import EVENT
from fossunited.utils.payments import (
    get_in_razorpay_money,
    get_razorpay_client,
)


class RazorpayPayment(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amount: DF.Currency
        billing_address: DF.Text | None
        buyer_name: DF.Data | None
        company_name: DF.Data | None
        currency: DF.Literal["INR"]  # noqa: F821
        document_name: DF.DynamicLink | None
        document_type: DF.Link | None
        email: DF.Data
        gstn: DF.Data | None
        meta_data: DF.Code | None
        order_id: DF.Data | None
        payment_id: DF.Data | None
        refund_id: DF.Data | None
        state: DF.Data | None
        status: DF.Literal[
            "Captured",  # noqa: F821
            "Failed",  # noqa: F821
            "Pending",  # noqa: F821
            "Refund Pending",  # noqa: F722, F821
            "Refunded",  # noqa: F722, F821
        ]

    # end: auto-generated types

    @frappe.whitelist()
    def refund(self):
        frappe.only_for("System Manager")

        if not self.is_paid:
            frappe.throw("Refunds Can be Made Only on Captured Payments!")

        client = get_razorpay_client()
        refund_amount = int(get_in_razorpay_money(self.amount))
        refund = client.payment.refund(self.payment_id, refund_amount)

        self.refund_id = refund["id"]
        if refund["status"] == "processed":
            self.status = "Refunded"
        elif refund["status"] == "pending":
            self.status = "Refund Pending"

        self.save()

        return refund["status"]

    @frappe.whitelist()
    def sync_status(self):
        client = get_razorpay_client()
        order = client.order.fetch(self.order_id)
        payments = client.order.payments(self.order_id).get("items", [])

        if order["status"] == "paid":
            frappe.errprint(payments)
            if payments[0]["status"] == "captured" and self.status != "Captured":
                self.status = "Captured"
                self.payment_id = payments[0]["id"]
                self.save()
            elif payments[0]["status"] == "refunded":
                self.status = "Refunded"
                self.save()

    @property
    def is_paid(self):
        return self.status == "Captured"

    def before_insert(self):
        if self.document_type == EVENT:
            is_ticket_live = frappe.db.get_value(
                EVENT, {"name": self.document_name}, "tickets_status"
            )
            if not bool(is_ticket_live):
                frappe.throw("Ticket sale are closed for this event!", frappe.PermissionError)

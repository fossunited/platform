# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import json

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.doctype_ids import EVENT, EVENT_RSVP, RSVP_RESPONSE


class FOSSEventRSVP(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.foss_custom_question.foss_custom_question import (
            FOSSCustomQuestion,
        )

        allow_edit: DF.Check
        chapter: DF.Data | None
        custom_questions: DF.Table[FOSSCustomQuestion]
        event: DF.Link
        event_name: DF.Data | None
        is_published: DF.Check
        max_rsvp_count: DF.Int
        requires_host_approval: DF.Check
        route: DF.Data | None
        rsvp_count: DF.Int
        rsvp_description: DF.TextEditor | None
    # end: auto-generated types

    def before_save(self):
        self.set_route()
        self.enable_rsvp_tab()

    def on_update(self):
        if int(self.rsvp_count) >= int(self.max_rsvp_count):
            self.is_published = 0

    def get_context(self, context):
        context.event = frappe.get_doc(EVENT, self.event)
        context.event_name = self.event_name
        context.event_date = context.event.event_start_date.strftime("%B %d, %Y")

        form_fields = [
            {
                "fieldname": "name1",
                "fieldtype": "Data",
                "label": "Full Name",
                "reqd": 1,
                "value": frappe.get_value("User", frappe.session.user, "full_name"),
            },
            {
                "fieldname": "email",
                "fieldtype": "Data",
                "label": "Email",
                "reqd": 1,
                "value": frappe.get_value("User", frappe.session.user, "email"),
            },
            {
                "fieldname": "im_a",
                "fieldtype": "Select",
                "label": "I'm a",
                "description": "Select your current profession",
                "options": "\nStudent\nProfessional\nOther",
                "reqd": 1,
            },
        ]
        form_fields.extend(self.get_custom_questions())
        context.form_fields = form_fields

        context.already_rsvp = True if self.check_if_already_rsvp() else False
        context.submission_doctype = RSVP_RESPONSE
        if context.already_rsvp:
            context.submission = frappe.db.get_value(
                RSVP_RESPONSE,
                {
                    "linked_rsvp": self.name,
                    "submitted_by": frappe.session.user,
                },
            )

        context.no_cache = 1

    def set_route(self):
        event_route = frappe.db.get_value(EVENT, self.event, "route")
        self.route = f"{event_route}/rsvp"

    def enable_rsvp_tab(self):
        frappe.db.set_value(EVENT, self.event, "show_rsvp", 1)

    def get_custom_questions(self):
        custom_questions = []
        for index, question in enumerate(self.custom_questions, start=1):
            custom_questions.append(
                {
                    "fieldname": "custom_question_" + str(index),
                    "fieldtype": question.type,
                    "label": question.question,
                    "options": question.options,
                    "reqd": question.is_mandatory or 0,
                    "description": question.description,
                }
            )
        return custom_questions

    def check_if_already_rsvp(self):
        return frappe.db.exists(
            RSVP_RESPONSE,
            {
                "linked_rsvp": self.name,
                "submitted_by": frappe.session.user,
            },
        )


@frappe.whitelist(allow_guest=True)
def create_rsvp(fields):
    fields = json.loads(fields)

    linked_rsvp_exists = frappe.db.exists(EVENT_RSVP, fields.get("linked_rsvp"))
    if not linked_rsvp_exists:
        frappe.throw("Invalid RSVP ID.", frappe.DoesNotExistError)

    fields.update(
        {
            "doctype": RSVP_RESPONSE,
            "submitted_by": (
                frappe.session.user
                if frappe.session.user not in ("Guest", "Administrator")
                else ""
            ),
        }
    )

    doc = frappe.get_doc(fields)
    doc.insert(ignore_permissions=True)
    return doc

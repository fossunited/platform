# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.doctype_ids import EVENT, EVENT_CFP, GLOBAL_CFP_SETTINGS, PROPOSAL


class FOSSEventCFP(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.foss_custom_question.foss_custom_question import (
            FOSSCustomQuestion,
        )
        from fossunited.fossunited.doctype.foss_event_cfp_reviewer.foss_event_cfp_reviewer import (
            FOSSEventCFPReviewer,
        )

        allow_cfp_edit: DF.Check
        anonymise_proposals: DF.Check
        cfp_custom_questions: DF.Table[FOSSCustomQuestion]
        cfp_form_description: DF.TextEditor | None
        cfp_reviewers: DF.Table[FOSSEventCFPReviewer]
        chapter: DF.Data | None
        deadline: DF.Datetime | None
        event: DF.Link
        event_name: DF.Data | None
        is_published: DF.Check
        only_talk_proposals: DF.Check
        only_workshops: DF.Check
        route: DF.Data | None
        status: DF.Literal["Closed", "Live"]  # noqa: F821
    # end: auto-generated types

    def before_insert(self):
        self.assign_reviewers()

    def assign_reviewers(self):
        reviewers = frappe.get_single(GLOBAL_CFP_SETTINGS).members
        for reviewer in reviewers:
            self.append(
                "cfp_reviewers",
                {
                    "reviewer": reviewer.profile,
                    "email": reviewer.email,
                    "full_name": reviewer.full_name,
                },
            )

    def before_save(self):
        self.set_route()
        self.enable_cfp_tab()

    def set_route(self):
        event_route = frappe.db.get_value(EVENT, self.event, "route")
        self.route = f"{event_route}/cfp"

    def enable_cfp_tab(self):
        frappe.db.set_value(EVENT, self.event, "show_cfp", 1)

    def get_context(self, context):
        context.submissions = get_cfp_submissions(self.name)
        context.event = frappe.get_doc(EVENT, self.event)
        context.event_name = self.event_name
        context.event_date = frappe.db.get_value(EVENT, self.event, "event_start_date").strftime(
            "%B %d, %Y"
        )
        context.submission_doctype = PROPOSAL
        context.already_submitted = True if self.check_if_already_submitted() else False

        context.form_fields = self.get_form_fields()
        context.no_cache = 1

    def get_form_fields(self):
        try:
            last_doc = frappe.get_last_doc(
                PROPOSAL,
                filters={"submitted_by": frappe.session.user},
            )
        except frappe.exceptions.DoesNotExistError:
            last_doc = {}

        meta = frappe.get_meta(PROPOSAL).as_dict()
        current_section = None

        form_fields = [
            {
                "fieldname": "full_name",
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
                "fieldname": "picture_url",
                "fieldtype": "Data",
                "label": "Picture (URL)",
                "value": last_doc.get("picture_url") or "",
                "description": (
                    "Paste a URL for your publicly hosted photo. Keep it in a 1:1 ratio."
                ),
                "reqd": 1,
            },
            {
                "fieldname": "designation",
                "fieldtype": "Data",
                "label": "Designation",
                "reqd": 1,
                "value": last_doc.get("designation") or "",
            },
            {
                "fieldname": "organization",
                "fieldtype": "Data",
                "label": "Organization",
                "value": last_doc.get("organization") or "",
            },
            {
                "fieldname": "bio",
                "fieldtype": "Text Editor",
                "label": "Speaker Bio",
                "reqd": 1,
                "value": last_doc.get("bio") or "",
            },
        ]
        for field in meta["fields"]:
            if field["fieldtype"] == "Column Break":
                continue
            if field["fieldtype"] == "Section Break":
                current_section = field["label"]
                continue
            if current_section in [
                "Meta Info",
                "Personal Information",
                "Custom Answers",
                "CFP Reviews",
                "Review Scores",
            ]:
                continue
            form_fields.append({k: v for k, v in field.items()})

        form_fields.extend(self.get_custom_questions())

        return form_fields

    def get_custom_questions(self):
        custom_questions = []
        for index, question in enumerate(self.cfp_custom_questions, start=1):
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

    def check_if_already_submitted(self):
        return frappe.db.exists(
            PROPOSAL,
            {
                "linked_cfp": self.name,
                "submitted_by": frappe.session.user,
            },
        )


@frappe.whitelist()
def create_cfp_submission(fields):
    if not frappe.db.exists(EVENT_CFP, frappe.parse_json(fields).get("linked_cfp")):
        frappe.throw("Invalid CFP ID.", frappe.DoesNotExistError)

    fields_dict = {
        "doctype": PROPOSAL,
        "submitted_by": frappe.session.user,
    }
    fields = frappe.parse_json(fields).update(fields_dict)
    doc = frappe.get_doc(fields)
    doc.insert(ignore_permissions=True)
    return doc


@frappe.whitelist()
def get_cfp_submissions(linked_cfp):
    submissions = frappe.get_all(
        PROPOSAL,
        fields=["*"],
        filters={
            "submitted_by": frappe.session.user,
            "linked_cfp": linked_cfp,
        },
    )
    frappe.form_dict["submissions"] = submissions
    return submissions

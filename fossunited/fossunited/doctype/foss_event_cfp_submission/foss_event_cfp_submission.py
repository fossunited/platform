# Copyright (c) 2023, Frappe x FOSSUnited and contributors
# For license information, please see license.txt
import frappe
from frappe.website.website_generator import WebsiteGenerator

from fossunited.api.emailing import add_to_email_group, create_email_group
from fossunited.doctype_ids import EVENT, EVENT_CFP, USER_PROFILE
from fossunited.fossunited.utils import get_doc_likes


class FOSSEventCFPSubmission(WebsiteGenerator):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from fossunited.fossunited.doctype.foss_custom_answer.foss_custom_answer import (
            FOSSCustomAnswer,
        )
        from fossunited.fossunited.doctype.foss_event_cfp_review.foss_event_cfp_review import (
            FOSSEventCFPReview,
        )

        approvability: DF.Data | None
        attendance_confirmed: DF.Check
        bio: DF.TextEditor
        chapter: DF.Data | None
        custom_answers: DF.Table[FOSSCustomAnswer]
        designation: DF.Data
        email: DF.Data
        event: DF.Data
        event_name: DF.Data | None
        first_name: DF.Data | None
        full_name: DF.Data
        is_first_talk: DF.Literal["Yes", "No"]  # noqa: F821
        is_published: DF.Check
        last_name: DF.Data | None
        linked_cfp: DF.Link
        negative_reviews: DF.Data | None
        organization: DF.Data | None
        picture_url: DF.Data | None
        positive_reviews: DF.Data | None
        reviews: DF.Table[FOSSEventCFPReview]
        route: DF.Data | None
        session_type: DF.Literal["Talk", "Lightning Talk", "Workshop"]  # noqa: F722, F821
        status: DF.Literal["Review Pending", "Screening", "Approved", "Rejected"]  # noqa: F722, F821
        submitted_by: DF.Link | None
        talk_description: DF.TextEditor
        talk_reference: DF.Data | None
        talk_title: DF.Data
        unsure_reviews: DF.Data | None
    # end: auto-generated types

    def before_insert(self):
        self.check_status()
        self.validate_linked_cfp_exists()

    def before_save(self):
        self.set_name()
        self.set_route()
        self.set_scores()
        self.handle_status_change()

    def after_insert(self):
        self.handle_email_group("CFP Proposers")

    def set_name(self):
        self.first_name = self.full_name.split(" ")[0]
        self.last_name = " ".join(self.full_name.split(" ")[1:])

    def set_route(self):
        event_route = frappe.db.get_value(EVENT, self.event, "route")
        self.route = f"{event_route}/cfp/{self.name}"

    def set_scores(self):
        statistics = self.get_review_statistics()
        self.positive_reviews = statistics[0]["percentage"]
        self.negative_reviews = statistics[1]["percentage"]
        self.unsure_reviews = statistics[2]["percentage"]
        self.approvability = statistics[3]["percentage"]

    def check_status(self):
        if self.status != "Review Pending":
            frappe.throw("Illegal status change", frappe.ValidationError)

    def validate_linked_cfp_exists(self):
        if not frappe.db.exists(EVENT_CFP, self.linked_cfp):
            frappe.throw("Invalid CFP", frappe.DoesNotExistError)

    def get_context(self, context):
        context.cfp = frappe.get_doc(EVENT_CFP, self.linked_cfp)
        context.event = frappe.get_doc(EVENT, self.event)
        context.likes = get_doc_likes(self.doctype, self.name)
        context.liked_by_user = frappe.session.user in context.likes
        context.reviewers = self.get_reviewers(context.cfp)
        context.is_reviewer = frappe.session.user in [
            reviewer["email"] for reviewer in context.reviewers
        ]
        context.nav_items = self.get_navbar_items(context)
        context.submitter_foss_profile = None

        if self.submitted_by:
            context.submitter_foss_profile = frappe.get_doc(
                USER_PROFILE, {"user": self.submitted_by}
            )

        context.review_statistics = self.get_review_statistics()
        context.reviews = self.get_reviews()
        context.already_reviewed = self.check_if_already_reviewed(context)

        context.remark_val = {
            "Yes": "Approved",
            "No": "Rejected",
            "Maybe": "Not Sure",
        }
        context.no_cache = 1

    def get_navbar_items(self, context):
        nav_items = [
            "proposal_details",
            "about_speaker",
            "proposal_reviews",
        ]

        if context.cfp.anonymise_proposals and not self.status == "Approved":
            nav_items.remove("about_speaker")

        return nav_items

    def get_reviewers(self, cfp):
        reviewers = []
        for reviewer in cfp.cfp_reviewers:
            reviewers.append(
                {
                    "full_name": reviewer.full_name,
                    "email": reviewer.email,
                    "profile": reviewer.reviewer,
                }
            )

        return reviewers

    def get_review_statistics(self):
        reviews = self.get_reviews()
        reviews_len = len(reviews) or 1

        score = {
            "Yes": 0,
            "No": 0,
            "Maybe": 0,
        }

        for review in reviews:
            score[review.to_approve] += 1

        score["approvability"] = (score["Yes"] / (reviews_len - score["Maybe"] or 1)) * 100

        statistics = [
            {
                "fieldname": "positive_reviews",
                "label": f'{score["Yes"]} People Approved this Proposal',
                "value": score["Yes"],
                "percentage": int((score["Yes"] / reviews_len) * 100),
                "color": "var(--clr-foss-mint-500)",
                "background": "var(--clr-foss-mint-50)",
            },
            {
                "fieldname": "negative_reviews",
                "label": f'{score["No"]} People Rejected this Proposal',
                "value": score["No"],
                "percentage": int((score["No"] / reviews_len) * 100),
                "color": "var(--clr-error-500)",
                "background": "var(--clr-error-50)",
            },
            {
                "fieldname": "unsure_reviews",
                "label": f'{score["Maybe"]} People Marked Unsure',
                "value": score["Maybe"],
                "percentage": int((score["Maybe"] / reviews_len) * 100),
                "color": "var(--clr-warning-500)",
                "background": "var(--clr-warning-50)",
            },
            {
                "fieldname": "approvability",
                "label": "Approvability of proposal",
                "value": "",
                "percentage": int(score["approvability"]),
                "color": "216, 97%, 42%",
                "background": "206, 100%, 97%",
            },
        ]

        return statistics

    def get_reviews(self):
        reviews = []
        for review in self.reviews:
            reviews.append(review)

        return reviews

    def get_review_templates(self):
        templates = frappe.get_doc("CFP Review Templates")
        templates_dict = {
            "Accepted": [],
            "Rejected": [],
            "Not Sure": [],
        }
        for template in templates.reviews_list:
            templates_dict[template.type].append(template.reason)

        return templates_dict

    def check_if_already_reviewed(self, context):
        for review in context.reviews:
            if review.email == frappe.session.user:
                return True

        return False

    def handle_status_change(self):
        if not self.has_value_changed("status"):
            return

        if self.status == "Approved":
            self.handle_email_group("Accepted Proposers")

        if self.status == "Rejected":
            self.handle_email_group("Rejected Proposers")

    def handle_email_group(self, type):
        if not frappe.db.exists(
            "Email Group",
            {
                "reference_document": self.event,
                "document_type": EVENT,
                "group_type": type,
            },
        ):
            create_email_group(
                type=type,
                reference_document=self.event,
                document_type=EVENT,
            )

        email_group = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.event,
                "document_type": EVENT,
                "group_type": type,
            },
            ["name"],
        )
        add_to_email_group(email_group, self.email)

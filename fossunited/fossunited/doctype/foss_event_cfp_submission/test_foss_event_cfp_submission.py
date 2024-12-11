import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_CFP,
    PROPOSAL,
)
from fossunited.tests.utils import insert_test_chapter, insert_test_event

fake = Faker()

LEAD = "test1@example.com"


class TestFOSSEventCFPSubmission(IntegrationTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter(lead_email=LEAD)
        self.event = insert_test_event(chapter=self.chapter)

        cfp = frappe.get_doc(
            {
                "doctype": EVENT_CFP,
                "event": self.event.name,
            }
        )
        cfp.insert()
        cfp.reload()
        self.cfp = cfp

        self.submission_email = fake.email()
        submission = frappe.get_doc(
            {
                "doctype": PROPOSAL,
                "linked_cfp": cfp.name,
                "full_name": fake.name(),
                "email": self.submission_email,
                "designation": "SDE",
                "bio": fake.text(),
                "talk_title": "Test Talk Title",
                "talk_description": fake.sentence(),
            }
        ).insert()
        submission.reload()

        self.submission = submission

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT_CFP, self.cfp.name, force=True)
        frappe.delete_doc(PROPOSAL, self.submission.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)

    def test_add_to_email_group(self):
        # given a cfp form
        cfp = self.cfp

        # When a submission is done by user
        submission = self.submission

        # Then the email should be added to an email group linked to event for CFP Proposers
        email_group = frappe.db.get_value(
            "Email Group", {"event": cfp.event, "group_type": "CFP Proposers"}
        )

        self.assertTrue(
            frappe.db.exists(
                "Email Group Member", {"email": submission.email, "email_group": email_group}
            )
        )

    def test_add_to_group_on_accept(self):
        # given a cfp and its submission
        cfp = self.cfp
        submission = self.submission

        frappe.set_user(LEAD)
        # When the status is changed to Approved
        submission.status = "Approved"
        submission.save()

        email_group = frappe.db.get_value(
            "Email Group", {"event": cfp.event, "group_type": "Accepted Proposers"}
        )
        # Then it should be added to an email group for this event, where type==Accepted Proposers
        self.assertTrue(
            frappe.db.exists(
                "Email Group Member", {"email": submission.email, "email_group": email_group}
            )
        )

    def test_add_to_group_on_reject(self):
        # given a cfp and its submission
        cfp = self.cfp
        submission = self.submission

        frappe.set_user(LEAD)
        # When the status is changed to Approved
        submission.status = "Rejected"
        submission.save()

        email_group = frappe.db.get_value(
            "Email Group", {"event": cfp.event, "group_type": "Rejected Proposers"}
        )
        # Then it should be added to an email group for this event, where type==Accepted Proposers
        self.assertTrue(
            frappe.db.exists(
                "Email Group Member", {"email": submission.email, "email_group": email_group}
            )
        )

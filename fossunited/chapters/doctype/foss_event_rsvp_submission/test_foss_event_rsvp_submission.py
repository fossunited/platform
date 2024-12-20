import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_RSVP
from fossunited.tests.utils import (
    insert_rsvp_form,
    insert_rsvp_submission,
    insert_test_chapter,
    insert_test_event,
)

fake = Faker()

WEBSITE_USER = "test2@example.com"


class TestFOSSEventRSVPSubmission(IntegrationTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter()
        self.event = insert_test_event(chapter=self.chapter)
        self.rsvp = insert_rsvp_form(event=self.event.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(EVENT_RSVP, self.rsvp.name, force=True)

    def test_unpublish_on_max_count(self):
        # Given an RSVP form with max count
        rsvp = self.rsvp

        # When submission count reaches the max count
        for _ in range(int(rsvp.max_rsvp_count)):
            insert_rsvp_submission(linked_rsvp=self.rsvp.name)

        # Then the RSVP must be unpublished
        is_published = frappe.db.get_value(EVENT_RSVP, rsvp.name, "is_published")
        self.assertFalse(is_published)

    def test_add_to_email_group(self):
        # Given an RSVP form for an event
        # When an RSVP response is done by a user
        frappe.set_user(WEBSITE_USER)
        insert_rsvp_submission(linked_rsvp=self.rsvp.name, email=WEBSITE_USER)

        # Then the email should be added to an email group linked to event for participants
        email_group = frappe.db.get_value(
            "Email Group", {"event": self.rsvp.event, "group_type": "Event Participants"}
        )

        self.assertTrue(
            frappe.db.exists(
                "Email Group Member", {"email": WEBSITE_USER, "email_group": email_group}
            )
        )

    def test_acceptance_workflow(self):
        # Given an RSVP form with accept all incoming responses
        rsvp = self.rsvp

        frappe.set_user(WEBSITE_USER)
        # When a submission is done
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)

        # Then the submission status should be accepted
        self.assertTrue(submission.status, "Accepted")

    def test_pending_workflow(self):
        # Given an rsvp with requires_host_approval = True
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        frappe.set_user(WEBSITE_USER)
        # When a submission is created
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)

        # Then the submission status should be pending
        self.assertTrue(submission.status, "Pending")

    def test_invalid_status_at_creation(self):
        # Given an rsvp with requires_host_approval = False
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        frappe.set_user(WEBSITE_USER)
        # When a submission is done with status accepted
        # Then a frappe.PermissionError should be raised
        with self.assertRaises(frappe.PermissionError):
            insert_rsvp_submission(linked_rsvp=rsvp.name, status="Accepted")

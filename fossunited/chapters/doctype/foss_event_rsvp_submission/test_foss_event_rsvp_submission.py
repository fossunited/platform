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
LEAD_USER = "test1@example.com"


class TestFOSSEventRSVPSubmission(IntegrationTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter()
        self.event = insert_test_event(chapter=self.chapter)
        self.rsvp = insert_rsvp_form(event=self.event.name)
        self.email_group = frappe.db.get_value(
            "Email Group",
            {
                "reference_document": self.rsvp.event,
                "document_type": EVENT,
                "group_type": "Event Participants",
            },
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(EVENT_RSVP, self.rsvp.name, force=True)

    def test_unpublish_on_max_count(self):
        # Given an RSVP form with max count
        rsvp = self.rsvp

        # We are using distinct emails here to avoid any unintended duplicate error.
        # So that we can insert the max count of submissions
        emails = set()
        while len(emails) < int(rsvp.max_rsvp_count):
            emails.add(fake.email())

        # When submission count reaches the max count
        for email in emails:
            insert_rsvp_submission(linked_rsvp=self.rsvp.name, email=email)

        # Then the RSVP must be unpublished
        is_published = frappe.db.get_value(EVENT_RSVP, rsvp.name, "is_published")
        self.assertFalse(is_published)

    def test_add_to_email_group(self):
        # Given an RSVP form for an event
        # When an RSVP response is done by a user
        frappe.set_user("Guest")
        insert_rsvp_submission(linked_rsvp=self.rsvp.name, email=WEBSITE_USER)

        # Then the email should be added to an email group linked to event for participants
        self.assertTrue(
            frappe.db.exists(
                "Email Group Member", {"email": WEBSITE_USER, "email_group": self.email_group}
            )
        )

    def test_acceptance_workflow(self):
        # Given an RSVP form with accept all incoming responses
        rsvp = self.rsvp

        frappe.set_user("Guest")
        # When a submission is done
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)

        # Then the submission status should be accepted
        self.assertTrue(submission.status, "Accepted")

    def test_pending_workflow(self):
        # Given an rsvp with requires_host_approval = True
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        frappe.set_user("Guest")
        # When a submission is created
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)

        # Then the submission status should be pending
        self.assertTrue(submission.status, "Pending")

    def test_pending_to_acceptance_workflow(self):
        # Given an rsvp with requires_host_approval = True
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        frappe.set_user("Guest")
        # When a submission is created
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)
        # The status should be pending
        self.assertTrue(submission.status, "Pending")

        # Now, as the chapter member,
        frappe.set_user("test1@example.com")
        # We know `test1@example.com` is a chapter member
        # because of how insert_test_chapter is implemented

        # When the submission is accepted
        submission.status = "Accepted"
        # Then it should save without any errors
        submission.save()

    def test_invalid_status_at_creation(self):
        # Given an rsvp with requires_host_approval = False
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        frappe.set_user("Guest")
        # When a submission is done with status accepted
        # Then a frappe.PermissionError should be raised
        with self.assertRaises(frappe.PermissionError):
            insert_rsvp_submission(linked_rsvp=rsvp.name, status="Accepted")

    def test_status_change_after_unpublish(self):
        # Given an RSVP form which requires host approval
        frappe.set_user(LEAD_USER)
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        # When a submission is done
        frappe.set_user("Guest")
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)

        # It should be saved with status as pending
        self.assertEqual(submission.status, "Pending")

        frappe.set_user(LEAD_USER)
        # When the RSVP form is unpublished
        rsvp.is_published = False
        rsvp.save()
        # and the lead user / system user try to make a change to status
        # Then the status should change without errors
        submission.status = "Rejected"
        submission.save()

    def test_add_to_email_on_acceptance(self):
        # Given an RSVP form which requires host approval
        frappe.set_user(LEAD_USER)
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        # When a submission is made
        frappe.set_user("Guest")
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)
        self.assertEqual(submission.status, "Pending")

        # Then the email should not be added to email group
        # When status is pending

        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

        # When status is changed to "Accepted"
        frappe.set_user(LEAD_USER)
        submission.status = "Accepted"
        submission.save()

        # Then the email should be added to email group
        self.assertTrue(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

    def test_no_add_to_email_on_rejection(self):
        # Given an RSVP form which requires host approval
        frappe.set_user(LEAD_USER)
        rsvp = self.rsvp
        rsvp.requires_host_approval = True
        rsvp.save()

        # When a submission is made
        frappe.set_user("Guest")
        submission = insert_rsvp_submission(linked_rsvp=rsvp.name)
        self.assertEqual(submission.status, "Pending")

        # Then the email should not be added to email group
        # When status is pending

        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

        # When status is changed to "Accepted"
        frappe.set_user(LEAD_USER)
        submission.status = "Rejected"
        submission.save()

        # Then the email should be added to email group
        self.assertFalse(
            frappe.db.exists(
                "Email Group Member",
                {
                    "email": submission.email,
                    "email_group": self.email_group,
                },
            )
        )

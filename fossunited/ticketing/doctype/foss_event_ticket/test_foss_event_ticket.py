import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.api.checkins import checkin_attendee
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_TICKET
from fossunited.tests.utils import generate_test_chapter, generate_test_event


class TestFOSSEventTicket(IntegrationTestCase):
    def setUp(self):
        self.lead_email = "test1@example.com"
        self.chapter = generate_test_chapter(lead_email=self.lead_email)
        self.event = generate_test_event(
            chapter=self.chapter, is_paid_event=True, tickets_status="Live"
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(EVENT, self.event.name, force=True)
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)

    def test_checkin(self):
        fake = Faker()

        # Given that a ticket is created for an event
        ticket = frappe.get_doc(
            {
                "doctype": EVENT_TICKET,
                "event": self.event.name,
                "full_name": fake.name(),
                "email": fake.email(),
                "tier": "General",
            }
        )
        ticket.insert(ignore_permissions=True)
        ticket.reload()

        # There should be no check-ins for that event
        self.assertFalse(ticket.check_ins)

        # Set the user as a chapter member
        frappe.set_user(self.lead_email)

        # When the user checks in the attendee
        checkin_attendee(self.event.name, ticket.as_dict(), self.lead_email)

        # Then the check-in data should be saved
        ticket.reload()
        self.assertTrue(ticket.check_ins)

        # When the user tries to check-in the attendee again on the same day
        # Then the user should not be able to check-in the attendee again
        with self.assertRaises(frappe.ValidationError):
            checkin_attendee(self.event.name, ticket.as_dict(), self.lead_email)

    def test_checkin_as_non_chapter_member(self):
        fake = Faker()

        # Given that a ticket is created for an event
        ticket = frappe.get_doc(
            {
                "doctype": EVENT_TICKET,
                "event": self.event.name,
                "full_name": fake.name(),
                "email": fake.email(),
                "tier": "General",
            }
        )
        ticket.insert(ignore_permissions=True)
        ticket.reload()

        self.assertFalse(ticket.check_ins)
        # Set the user as a random user
        frappe.set_user("test2@example.com")

        # When the user checks in the attendee
        # Then the user should not have permission to check-in the attendee
        with self.assertRaises(frappe.PermissionError):
            checkin_attendee(self.event.name, ticket.as_dict(), "test2@example.com")

import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.api.checkins import checkin_attendee
from fossunited.doctype_ids import CHAPTER, EVENT, EVENT_TICKET
from fossunited.tests.utils import insert_test_chapter, insert_test_event, insert_test_ticket


class TestFOSSEventTicket(IntegrationTestCase):
    def setUp(self):
        self.lead_email = "test1@example.com"
        self.chapter = insert_test_chapter(lead_email=self.lead_email)
        self.event = insert_test_event(
            chapter=self.chapter,
            is_paid_event=True,
            tickets_status="Live",
            tiers=[
                {
                    "enabled": 1,
                    "title": "Test",
                    "price": 100,
                    "maximum_tickets": 5,
                }
            ],
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

    def test_create_when_tickets_closed(self):
        # Given a paid event with ticket status as "Closed"
        self.event.tickets_status = "Closed"
        self.event.save()
        # When a ticket is created for this event
        # Then an error must be thrown
        with self.assertRaises(frappe.PermissionError):
            insert_test_ticket(event=self.event.name)

    def test_ticket_creation(self):
        # Given an event
        # When the tickets_status is Live
        self.event.tickets_status = "Live"
        self.event.save()

        # Then a ticket for this event should be created without any problem
        ticket = insert_test_ticket(event=self.event.name)
        ticket.delete(force=True)

    def test_ticket_tier_closing(self):
        # Given an event with a ticket tier
        tier = self.event.get("tiers")[0]

        # Make sure this tier is enabled
        self.assertTrue(tier.enabled)

        # make sure there are 0 tickets of this tier to start with
        self.assertEqual(
            frappe.db.count(
                EVENT_TICKET,
                {
                    "event": self.event.name,
                    "tier": tier.title,
                },
            ),
            0,
        )

        # When maximum number of tickets are created of this tier type
        tickets = []
        for _ in range(tier.maximum_tickets):
            _ticket = insert_test_ticket(
                event=self.event.name,
                tier=tier.title,
            )
            tickets.append(_ticket)

        self.event.reload()

        # Then the tier should be disabled
        tier = self.event.get("tiers")[0]
        self.assertEqual(tier.enabled, 0)

        for ticket in tickets:
            ticket.delete(force=1)

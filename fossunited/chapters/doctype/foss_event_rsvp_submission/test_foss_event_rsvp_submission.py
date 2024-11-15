# Copyright (c) 2023, Frappe x FOSSUnited and Contributors
# See license.txt

from datetime import datetime, timedelta

import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import EVENT, EVENT_RSVP, RSVP_RESPONSE

fake = Faker()

WEBSITE_USER = "test2@example.com"


class TestFOSSEventRSVPSubmission(IntegrationTestCase):
    def setUp(self):
        event = frappe.get_doc(
            {
                "doctype": EVENT,
                "event_name": fake.name(),
                "event_permalink": fake.slug(),
                "status": "Live",
                "event_type": "FOSS Meetup",
                "event_start_date": datetime.today(),
                "event_end_date": datetime.today() + timedelta(1),
                "event_description": "testing",
            }
        )
        event.insert()
        event.reload()
        self.event = event

        rsvp = frappe.get_doc(
            {
                "doctype": EVENT_RSVP,
                "max_rsvp_count": 5,
                "event": event.name,
            }
        )
        rsvp.insert()
        rsvp.reload()
        self.rsvp = rsvp

    def tearDown(self):
        frappe.delete_doc(EVENT, self.event.name, force=1)
        frappe.delete_doc(EVENT_RSVP, self.rsvp.name, force=1)

    def test_unpublish_on_max_count(self):
        # Given an RSVP form with max count
        rsvp = self.rsvp

        # When submission count reaches the max count
        for i in range(int(rsvp.max_rsvp_count)):
            frappe.get_doc(
                {
                    "doctype": RSVP_RESPONSE,
                    "linked_rsvp": rsvp.name,
                    "event": rsvp.event,
                    "name1": fake.name(),
                    "email": fake.email(),
                    "im_a": "Student",
                }
            ).insert()

        # Then the RSVP must be unpublished
        is_published = frappe.db.get_value(EVENT_RSVP, rsvp.name, "is_published")
        self.assertFalse(is_published)

    def test_add_to_email_group(self):
        # Given an RSVP form for an event
        form = self.rsvp

        frappe.set_user(WEBSITE_USER)
        # When an RSVP response is done by a user
        frappe.get_doc(
            {
                "doctype": RSVP_RESPONSE,
                "linked_rsvp": form.name,
                "event": form.event,
                "name1": fake.name(),
                "email": WEBSITE_USER,
                "im_a": "Student",
            }
        ).insert()

        # Then the email should be added to an email group linked to event for participants
        email_group = frappe.db.get_value(
            "Email Group", {"event": form.event, "group_type": "Event Participants"}
        )

        self.assertTrue(
            frappe.db.exists(
                "Email Group Member", {"email": WEBSITE_USER, "email_group": email_group}
            )
        )

        frappe.set_user("Administrator")

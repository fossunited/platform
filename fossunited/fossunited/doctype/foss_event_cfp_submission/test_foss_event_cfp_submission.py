from datetime import datetime, timedelta

import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import (
    CHAPTER,
    CITY_COMMUNITY,
    EVENT,
    EVENT_CFP,
    PROPOSAL,
    USER_PROFILE,
)

fake = Faker()

LEAD = "test1@example.com"


class TestFOSSEventCFPSubmission(IntegrationTestCase):
    def setUp(self):
        chapter = frappe.get_doc(
            {
                "doctype": CHAPTER,
                "chapter_name": fake.text(max_nb_chars=40),
                "chapter_type": CITY_COMMUNITY,
                "slug": fake.slug(),
                "city": "Pune",
                "country": "India",
                "email": fake.email(),
                "facebook": fake.url(),
                "instagram": fake.url(),
                "linkedin": fake.url(),
                "mastodon": fake.url(),
                "matrix": fake.url(),
                "state": "Maharashtra",
                "x": fake.url(),
            }
        )
        chapter.insert()
        chapter.reload()

        if not frappe.db.exists("Role", "Chapter Team Member"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Team Member"}).insert(
                ignore_permissions=True
            )
        if not frappe.db.exists("Role", "Chapter Lead"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Lead"}).insert(
                ignore_permissions=True
            )

        lead_profile = frappe.db.get_value(
            USER_PROFILE,
            {"user": LEAD},
            "name",
        )

        chapter.append(
            "chapter_members",
            {
                "chapter_member": lead_profile,
                "role": "Lead",
            },
        )
        chapter.save()
        chapter.reload()

        event = frappe.get_doc(
            {
                "doctype": EVENT,
                "chapter": chapter.name,
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

        cfp = frappe.get_doc(
            {
                "doctype": EVENT_CFP,
                "event": event.name,
            }
        )
        cfp.insert()
        cfp.reload()
        self.cfp = cfp

    def tearDown(self):
        frappe.delete_doc(EVENT, self.event.name, force=1)
        frappe.delete_doc(EVENT_CFP, self.cfp.name, force=1)

    def test_add_to_email_group(self):
        # given a cfp form
        cfp = self.cfp

        # when a submission is done by user
        response_email = fake.email()

        frappe.get_doc(
            {
                "doctype": PROPOSAL,
                "linked_cfp": cfp.name,
                "full_name": fake.name(),
                "email": response_email,
                "designation": "SDE",
                "bio": fake.text(),
                "talk_title": "Test Talk Title",
                "talk_description": fake.sentence(),
            }
        ).insert()

        # Then the email should be added to an email group linked to event for CFP Proposers
        email_group = frappe.db.get_value(
            "Email Group", {"event": cfp.event, "group_type": "CFP Proposers"}
        )

        self.assertTrue(
            frappe.db.exists(
                "Email Group Member", {"email": response_email, "email_group": email_group}
            )
        )

    def test_add_to_group_on_accept(self):
        # given a cfp and its submission
        cfp = self.cfp
        response_email = fake.email()

        submission = frappe.get_doc(
            {
                "doctype": PROPOSAL,
                "linked_cfp": cfp.name,
                "full_name": fake.name(),
                "email": response_email,
                "designation": "SDE",
                "bio": fake.text(),
                "talk_title": "Test Talk Title",
                "talk_description": fake.sentence(),
            }
        )
        submission.insert()
        submission.reload()

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
                "Email Group Member", {"email": response_email, "email_group": email_group}
            )
        )

        frappe.set_user("Administrator")

    def test_add_to_group_on_reject(self):
        # given a cfp and its submission
        cfp = self.cfp
        response_email = fake.email()

        submission = frappe.get_doc(
            {
                "doctype": PROPOSAL,
                "linked_cfp": cfp.name,
                "full_name": fake.name(),
                "email": response_email,
                "designation": "SDE",
                "bio": fake.text(),
                "talk_title": "Test Talk Title",
                "talk_description": fake.sentence(),
            }
        )
        submission.insert()
        submission.reload()

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
                "Email Group Member", {"email": response_email, "email_group": email_group}
            )
        )

        frappe.set_user("Administrator")

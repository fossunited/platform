import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.api.emailing import (
    add_to_email_group,
    create_newsletter_campaign,
    send_campaign,
    send_test_email,
)
from fossunited.doctype_ids import CHAPTER, EMAIL_GROUP, EVENT

from .utils import insert_test_chapter, insert_test_event

fake = Faker()


class TestEmailing(IntegrationTestCase):
    def setUp(self):
        self.lead_email = "test1@example.com"
        self.chapter = insert_test_chapter(lead_email=self.lead_email)
        self.event = insert_test_event(chapter=self.chapter)

        self.setup_campaign()

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)

    def setup_campaign(self):
        email_group = frappe.get_doc(
            EMAIL_GROUP, {"event": self.event.name, "group_type": "Event Participants"}
        )

        recipient_emails = ["test2@example.com", "test3@example.com", "test5@example.com"]
        for email in recipient_emails:
            add_to_email_group(email_group.name, email)

        recipient_groups = [
            {
                "label": email_group.group_type,
                "value": email_group.name,
                "description": "",
            }
        ]
        newsletter_data = {
            "subject": fake.sentence(),
            "content_type": "Rich Text",
            "message": fake.paragraph(),
            "email_group": recipient_groups,
            "attachments": [],
        }
        self.newsletter = create_newsletter_campaign(
            data=newsletter_data, event=self.event.name, chapter=self.chapter.name
        )

    def test_send_test_email(self):
        frappe.set_user(self.lead_email)

        test_email = fake.email()

        send_test_email(self.newsletter.name, test_email)

    def test_send_campaign(self):
        frappe.set_user(self.lead_email)

        send_campaign(self.newsletter.name)

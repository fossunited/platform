import frappe
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import EMAIL_GROUP, HACKATHON
from fossunited.tests.utils import insert_test_chapter, insert_test_hackathon


class TestFOSSHackathon(IntegrationTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter()
        self.hackathon = insert_test_hackathon(chapter=self.chapter.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        self.chapter.delete(force=True)
        self.hackathon.delete(force=True)

    def test_hackathon_route(self):
        if self.hackathon.permalink:
            self.assertEqual(self.hackathon.route, f"hack/{self.hackathon.permalink}")
        else:
            self.assertEqual(
                self.hackathon.route,
                f"hack/{self.hackathon.hackathon_name.lower().replace(' ', '-')}",
            )

    def test_email_group_creation_on_create(self):
        # When the self.hackathon was created
        # An email group must have been created linked to this hackathon
        self.assertIsNotNone(
            frappe.db.exists(
                EMAIL_GROUP,
                {
                    "document_type": HACKATHON,
                    "reference_document": self.hackathon.name,
                    "group_type": "Event Participants",
                },
            )
        )
        # Asserting that there's only 1 email group of document type Hackathon
        self.assertEqual(frappe.db.count(EMAIL_GROUP, {"document_type": HACKATHON}), 1)

        # When a new hackathon is created
        new_hackathon = insert_test_hackathon(chapter=self.chapter.name)
        # Then a new email group linked to this new hackathon must be created
        self.assertIsNotNone(
            frappe.db.exists(
                EMAIL_GROUP,
                {
                    "document_type": HACKATHON,
                    "reference_document": new_hackathon.name,
                    "group_type": "Event Participants",
                },
            )
        )
        # Assert that the email group count increases for document type of Hackathon
        self.assertEqual(frappe.db.count(EMAIL_GROUP, {"document_type": HACKATHON}), 2)

        new_hackathon.delete(force=True)

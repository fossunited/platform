import frappe
from frappe.tests import IntegrationTestCase

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

import frappe
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import HACKATHON
from fossunited.tests.utils import insert_test_hackathon


class TestFOSSHackathon(IntegrationTestCase):
    def setUp(self):
        self.hackathon = insert_test_hackathon()

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.delete_doc(HACKATHON, self.hackathon.name, force=True)

    def test_hackathon_route(self):
        if self.hackathon.permalink:
            self.assertTrue(self.hackathon.route == f"hack/{self.hackathon.permalink}")
        else:
            self.assertTrue(
                self.hackathon.route
                == f"hack/{self.hackathon.hackathon_name.lower().replace(' ', '-')}"
            )

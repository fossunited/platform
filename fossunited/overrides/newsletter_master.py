import frappe
from frappe.email.doctype.newsletter.newsletter import Newsletter
from frappe.utils import random_string


class NewsletterMaster(Newsletter):
    def autoname(self):
        random_string = get_random_string()
        while bool(frappe.db.exists("Newsletter", random_string)):
            random_string = get_random_string()

        self.name = random_string


def get_random_string():
    return random_string(10).lower()

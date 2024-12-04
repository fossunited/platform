import frappe
from frappe.email.doctype.newsletter.newsletter import Newsletter
from frappe.utils import random_string


class NewsletterExtend(Newsletter):
    """
    An extended Newsletter class that generates unique identifiers for newsletter documents.

    This class inherits from the base Newsletter class and overrides the naming mechanism
    to ensure each newsletter has a unique identifier.

    By default, the name of a newsletter is set to the subject, which can lead to conflicts.
    This extended class addresses this issue by providing a custom naming scheme.

    Attributes:
        Inherits all attributes from the base Newsletter class.
    """

    def autoname(self):
        unique_code = self.generate_unique_newsletter_code()
        self.name = unique_code

    def generate_unique_newsletter_code(self):
        """
        Generate a unique code for the newsletter.

        Returns:
            str: A unique 10-character lowercase string
        """
        code = random_string(10).lower()
        while frappe.db.exists("Newsletter", code):
            code = random_string(10).lower()
        return code

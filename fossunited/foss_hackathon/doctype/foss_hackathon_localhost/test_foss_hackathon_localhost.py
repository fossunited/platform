import frappe
import frappe.permissions
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import (
    USER_PROFILE,
)
from fossunited.tests.utils import (
    insert_test_chapter,
    insert_test_hackathon,
    insert_test_hackathon_localhost,
)


class TestFOSSHackathonLocalHost(IntegrationTestCase):
    def setUp(self):
        self.ORGANIZER_1 = "test1@example.com"
        self.organizer1_profile = frappe.get_doc(USER_PROFILE, {"user": self.ORGANIZER_1})
        self.ORGANIZER_2 = "test2@example.com"
        self.organizer2_profile = frappe.get_doc(USER_PROFILE, {"user": self.ORGANIZER_2})
        self.chapter = insert_test_chapter()
        self.hackathon = insert_test_hackathon(chapter=self.chapter.name)
        self.localhost = insert_test_hackathon_localhost(parent_hackathon=self.hackathon.name)

    def tearDown(self):
        frappe.set_user("Administrator")
        self.chapter.delete(force=True)
        self.localhost.delete(force=True)
        self.hackathon.delete(force=True)

    def test_role_assignment_on_create(self):
        # Given, two users who are not a part of any localhost
        # they should not be having the "Localhost Organizer" Role.
        self.assertFalse(self.has_organizer_role(self.ORGANIZER_1))
        self.assertFalse(self.has_organizer_role(self.ORGANIZER_2))

        # When a localhost is created with them as organizers
        new_localhost = insert_test_hackathon_localhost(
            parent_hackathon=self.hackathon.name,
            organizers=[
                {
                    "profile": self.organizer1_profile.name,
                },
                {
                    "profile": self.organizer2_profile.name,
                },
            ],
        )

        # Then, they should have the "Localhost Organizer" Role.
        self.assertTrue(self.has_organizer_role(self.ORGANIZER_1))
        self.assertTrue(self.has_organizer_role(self.ORGANIZER_2))
        new_localhost.delete(force=True)

    def test_role_deassignment(self):
        # Add Organizer 1 to self.localhost
        self.localhost.append(
            "organizers",
            {
                "profile": self.organizer1_profile.name,
            },
        )
        # Add Organizer 2 to self.localhost
        self.localhost.append(
            "organizers",
            {
                "profile": self.organizer2_profile.name,
            },
        )
        self.localhost.save()

        self.assertTrue(self.has_organizer_role(self.ORGANIZER_1))
        self.assertTrue(self.has_organizer_role(self.ORGANIZER_2))

        # Remove organizer 2 from self.localhost
        for member in self.localhost.organizers:
            if member.profile == self.organizer2_profile.name:
                self.localhost.organizers.remove(member)
                break

        self.localhost.save()
        self.assertEqual(len(self.localhost.organizers), 1)
        # Organizer 2 should not have the "Localhost Organizer" Role
        self.assertFalse(self.has_organizer_role(self.ORGANIZER_2))

    def test_role_deassign_on_trash(self):
        # Add Organizer 1 to self.localhost
        self.localhost.append(
            "organizers",
            {
                "profile": self.organizer1_profile.name,
            },
        )
        self.localhost.save()

        # Organizer 1 should have the "Localhost Organizer" Role
        self.assertTrue(self.has_organizer_role(self.ORGANIZER_1))
        # When self.localhost is trashed
        self.localhost.delete(force=True)
        # Then Organizer 1 should not have the "Localhost Organizer" Role
        self.assertFalse(self.has_organizer_role(self.ORGANIZER_1))

    def test_handle_assignment_deassignment_together(self):
        """
        Test that roles are handled correctly when same
        number of organizers are added and removed simultaneously
        """
        # Add Organizer 1 to self.localhost
        self.localhost.append(
            "organizers",
            {
                "profile": self.organizer1_profile.name,
            },
        )
        self.localhost.save()

        self.assertTrue(self.has_organizer_role(self.ORGANIZER_1))

        # Remove organizer 1 from self.localhost
        for member in self.localhost.organizers:
            if member.profile == self.organizer1_profile.name:
                self.localhost.organizers.remove(member)
                break
        # Before save, add Organizer 2 to self.localhost
        self.localhost.append(
            "organizers",
            {
                "profile": self.organizer2_profile.name,
            },
        )
        self.localhost.save()
        self.assertFalse(self.has_organizer_role(self.ORGANIZER_1))
        self.assertTrue(self.has_organizer_role(self.ORGANIZER_2))

    def test_other_localhost_member(self):
        # Add Organizer 1 to self.localhost
        self.localhost.append(
            "organizers",
            {
                "profile": self.organizer1_profile.name,
            },
        )
        self.localhost.save()

        self.assertTrue(self.has_organizer_role(self.ORGANIZER_1))

        # Create another localhost with Organizer 1 as an organizer
        new_localhost = insert_test_hackathon_localhost(
            parent_hackathon=self.hackathon.name,
            organizers=[
                {
                    "profile": self.organizer1_profile.name,
                },
            ],
        )

        # Remove Organizer 1 from self.localhost
        for member in self.localhost.organizers:
            if member.profile == self.organizer1_profile.name:
                self.localhost.organizers.remove(member)
                break

        self.localhost.save()

        # Organizer 1 should still have the "Localhost Organizer" Role
        self.assertTrue(self.has_organizer_role(self.ORGANIZER_1))
        new_localhost.delete(force=True)

    def has_organizer_role(self, user):
        roles = frappe.get_roles(user)
        if "Localhost Organizer" in roles:
            return True

        return False

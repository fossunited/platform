# Copyright (c) 2023, Frappe x FOSSUnited and Contributors
# See license.txt
import uuid

import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import USER_PROFILE
from fossunited.foss_profiles.doctype.foss_user_profile.foss_user_profile import (
    PrivateProfileError,
)

fake = Faker()


class TestFOSSUserProfile(IntegrationTestCase):
    def test_add_profile(self):
        # Given a user that does not have a FOSSUnitedProfile
        inserted_username = fake.user_name()
        inserted_name = fake.name()
        profile_exists = frappe.db.exists(USER_PROFILE, {"username": inserted_username})
        self.assertFalse(profile_exists)

        # When a FOSSUnitedProfile is created for the user
        # Note that a Frappe User needs to exist before a Profile can be created
        # Verify that only required values are provided below
        frappe_user = frappe.get_doc(
            {
                "doctype": "User",
                # Create a unique email address as it is used as a database key
                "email": str(uuid.uuid4()) + "@fossunited.org",
                "first_name": inserted_name.split(" ")[0],
                "name": inserted_name,
                "full_name": inserted_name,
            },
        ).insert()

        # Then verify that the Profile has been stored as expected
        profile_exists = frappe.db.exists(USER_PROFILE, {"user": frappe_user.name})

        self.assertTrue(profile_exists)

    def test_private_profile_access(self):
        test_name = fake.name()
        test_user = frappe.get_doc(
            {
                "doctype": "User",
                "email": str(uuid.uuid4()) + "@fossunited.org",
                "first_name": test_name.split(" ")[0],
                "name": test_name,
                "full_name": test_name,
            },
        ).insert()

        # Given a private profile
        private_profile = frappe.get_doc(USER_PROFILE, {"user": test_user.name})
        frappe.db.set_value(USER_PROFILE, private_profile.name, "is_private", "1")

        current_user = frappe.session.user
        frappe.set_user("guest@example.com")

        with self.assertRaises(PrivateProfileError) as context:
            # When accessing the profile not as admin or user
            # then an exception is raised
            private_profile = frappe.get_doc(USER_PROFILE, {"user": test_user.name})
            # Simulate loading the profile
            private_profile.get_context({})

        self.assertTrue("Profile is Private" in str(context.exception))

        frappe.set_user(current_user)
        frappe.delete_doc(USER_PROFILE, private_profile.name)
        frappe.delete_doc("User", test_user.name)

    def test_profile_route(self):
        # When a user profile is created
        # Then the route for that profile should be of format: u/<username>
        test_email = fake.email()
        test_user = frappe.get_doc(
            {
                "doctype": "User",
                "email": test_email,
                "first_name": fake.name().split()[0],
            },
        ).insert()

        test_user.reload()

        profile = frappe.get_doc(USER_PROFILE, {"user": test_user.name})
        profile.username = fake.user_name()
        profile.save(ignore_permissions=True)

        profile.reload()

        self.assertTrue(profile.route == f"u/{profile.username}")

        profile.delete(force=1)
        test_user.delete(force=1)

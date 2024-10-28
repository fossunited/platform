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


class TestFOSSUserProfile(IntegrationTestCase):
    def test_add_profile(self):
        # Given a user that does not have a FOSSUnitedProfile
        fake = Faker()
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
        fake = Faker()
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

        private_profile = frappe.get_doc(
            {
                "doctype": USER_PROFILE,
                "user": test_user.name,
                "is_private": 1,
                "username": fake.user_name(),
            }
        ).insert()

        current_user = frappe.session.user
        frappe.set_user("guest@example.com")

        with self.assertRaises(PrivateProfileError) as context:
            private_profile.get_profile()

        self.assertTrue("Profile is Private" in str(context.exception))

        frappe.set_user(current_user)
        frappe.delete_doc(USER_PROFILE, private_profile.name)
        frappe.delete_doc("User", test_user.name)

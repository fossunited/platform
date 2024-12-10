import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import CHAPTER, USER_PROFILE
from fossunited.tests.utils import insert_test_chapter

fake = Faker()


class TestFOSSChapter(IntegrationTestCase):
    def setUp(self):
        self.chapter = insert_test_chapter()

    def tearDown(self):
        frappe.delete_doc(CHAPTER, self.chapter.name, force=1)

    def test_role_assignment_on_create(self):
        # Given a chapter
        chapter = self.chapter

        # When the chapter was created, a lead was assigned to it.
        # Then the lead should have the role of 'Chapter Lead' and 'Chapter Team Member'
        user = frappe.db.get_value(USER_PROFILE, chapter.chapter_members[0].chapter_member, "user")
        has_role = frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})
        self.assertTrue(has_role)

    def test_role_assignment_on_member_addition(self):
        # Given a chapter: self.chapter
        chapter = frappe.get_doc(CHAPTER, self.chapter.name)

        # When a new member is added to the chapter
        new_member = frappe.get_doc(USER_PROFILE, {"user": "test1@example.com"})

        chapter.append(
            "chapter_members", {"chapter_member": new_member.name, "role": "Core Team Member"}
        )
        chapter.save()

        # Then the new member should have the role of 'Chapter Team Member'
        user = frappe.db.get_value(USER_PROFILE, new_member.name, "user")
        has_role = frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})
        self.assertTrue(has_role)

    def test_role_deassignment_on_member_removal(self):
        # Given a chapter: self.chapter
        chapter = frappe.get_doc(CHAPTER, self.chapter.name)

        new_members = frappe.get_all(
            USER_PROFILE,
            filters=[
                ["user", "like", "%test%"],
                ["name", "not in", [m.chapter_member for m in chapter.chapter_members]],
            ],
        )
        for new_member in new_members:
            chapter.append(
                "chapter_members", {"chapter_member": new_member.name, "role": "Core Team Member"}
            )
        chapter.save()

        # When a member is removed from the chapter
        removed_member = chapter.chapter_members[0]
        chapter.chapter_members = [
            m for m in chapter.chapter_members if m.chapter_member != removed_member.chapter_member
        ]
        chapter.save()

        # Then the removed member should not have the role of 'Chapter Team Member'
        user = frappe.db.get_value(USER_PROFILE, removed_member.chapter_member, "user")
        has_role = frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})

        # check other members retain the role
        for member in chapter.chapter_members:
            user = frappe.db.get_value(USER_PROFILE, member.chapter_member, "user")
            if not bool(
                frappe.db.exists("Has Role", {"role": "Chapter Team Member", "parent": user})
            ):
                self.fail(f"Role not retained for {member}")

        self.assertFalse(has_role)

    def test_unique_chapter_slug(self):
        # Given a chapter: self.chapter
        chapter = self.chapter

        # When a new chapter is created with the same slug
        # Then an exception should be raised
        with self.assertRaises(frappe.UniqueValidationError):
            insert_test_chapter(slug=chapter.slug)

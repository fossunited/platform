import frappe
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import (
    CHAPTER,
    EVENT,
    EVENT_VOLUNTEER,
)
from fossunited.tests.utils import insert_test_chapter, insert_test_event


class TestFOSSChapterEvent(IntegrationTestCase):
    def setUp(self):
        self.lead = "test1@example.com"
        self.chapter = insert_test_chapter(lead_email=self.lead)
        self.event = insert_test_event(
            chapter=self.chapter,
        )

    def tearDown(self):
        frappe.delete_doc(CHAPTER, self.chapter.name, force=True)
        frappe.delete_doc(EVENT, self.event.name, force=True)

    def test_members_are_added_to_event(self):
        # Given a chapter
        chapter = self.chapter

        # When an event is created for the chapter
        event = self.event

        # Then the existing members of the chapter should be added to the event
        for member in chapter.chapter_members:
            self.assertTrue(
                frappe.db.exists(
                    EVENT_VOLUNTEER,
                    {
                        "parent": event.name,
                        "member": member.chapter_member,
                    },
                )
            )

    def test_unique_event_slug(self):
        """Test that event slugs must be unique within a chapter
        but can be reused across chapters."""

        original_chapter = self.chapter
        original_event = self.event
        existing_permalink = original_event.event_permalink

        # Test 1: Same chapter, same slug (should fail)
        with self.assertRaises(frappe.exceptions.ValidationError):
            insert_test_event(chapter=original_chapter, event_permalink=existing_permalink)

        # Test 2: Different chapter, same slug (should succeed)
        new_chapter = insert_test_chapter(city="Kochi", state="Kerala")

        insert_test_event(
            chapter=new_chapter,
            event_permalink=existing_permalink,
        )

        # Test 3: Same chapter, different slug (should succeed)
        insert_test_event(chapter=original_chapter)

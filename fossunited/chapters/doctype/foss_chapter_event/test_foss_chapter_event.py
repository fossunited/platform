from datetime import datetime, timedelta

import frappe
from faker import Faker
from frappe.tests import IntegrationTestCase

from fossunited.doctype_ids import (
    CHAPTER,
    CITY_COMMUNITY,
    EVENT,
    EVENT_VOLUNTEER,
    USER_PROFILE,
)

fake = Faker()

LEAD = "test1@example.com"
MEMBER1 = "test2@example.com"


class TestFOSSChapterEvent(IntegrationTestCase):
    def setUp(self):
        chapter = frappe.get_doc(
            {
                "doctype": CHAPTER,
                "chapter_name": fake.text(max_nb_chars=40),
                "chapter_type": CITY_COMMUNITY,
                "slug": fake.slug(),
                "city": "Pune",
                "country": "India",
                "email": fake.email(),
                "facebook": fake.url(),
                "instagram": fake.url(),
                "linkedin": fake.url(),
                "mastodon": fake.url(),
                "matrix": fake.url(),
                "state": "Maharashtra",
                "x": fake.url(),
            }
        )
        chapter.insert()
        chapter.reload()

        if not frappe.db.exists("Role", "Chapter Team Member"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Team Member"}).insert(
                ignore_permissions=True
            )
        if not frappe.db.exists("Role", "Chapter Lead"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Lead"}).insert(
                ignore_permissions=True
            )

        lead_profile = frappe.db.get_value(
            USER_PROFILE,
            {"user": LEAD},
            "name",
        )

        chapter.append(
            "chapter_members",
            {
                "chapter_member": lead_profile,
                "role": "Lead",
            },
        )
        chapter.save()

        self.chapter = chapter

        event = frappe.get_doc(
            {
                "doctype": EVENT,
                "chapter": chapter.name,
                "event_name": fake.text(max_nb_chars=40),
                "event_type": "FOSS Meetup",
                "event_permalink": fake.slug(),
                "status": "Live",
                "event_start_date": datetime.now() + timedelta(days=1),
                "event_end_date": datetime.now() + timedelta(days=2),
                "event_description": fake.text(max_nb_chars=200),
            }
        )
        event.insert()
        event.reload()
        self.event = event

    def tearDown(self):
        frappe.delete_doc(CHAPTER, self.chapter.name, force=1)
        frappe.delete_doc(EVENT, self.event.name, force=1)

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
        duplicate_event = frappe.get_doc(
            {
                "doctype": EVENT,
                "chapter": original_chapter.name,
                "event_name": fake.text(max_nb_chars=40),
                "event_type": "FOSS Meetup",
                "event_permalink": existing_permalink,
                "status": "Live",
                "event_start_date": datetime.now() + timedelta(days=4),
                "event_end_date": datetime.now() + timedelta(days=5),
                "event_description": fake.text(max_nb_chars=200),
            }
        )
        with self.assertRaises(frappe.exceptions.ValidationError):
            duplicate_event.insert()

        # Test 2: Different chapter, same slug (should succeed)
        new_chapter = frappe.get_doc(
            {
                "doctype": CHAPTER,
                "chapter_name": fake.text(max_nb_chars=40),
                "chapter_type": CITY_COMMUNITY,
                "slug": fake.slug(),
                "city": "Kochi",
                "country": "India",
                "email": fake.email(),
                "facebook": fake.url(),
                "instagram": fake.url(),
                "linkedin": fake.url(),
                "mastodon": fake.url(),
                "matrix": fake.url(),
                "state": "Kerala",
                "x": fake.url(),
            }
        )
        new_chapter.insert()
        new_chapter.reload()

        cross_chapter_event = frappe.get_doc(
            {
                "doctype": EVENT,
                "chapter": new_chapter.name,
                "event_name": fake.text(max_nb_chars=40),
                "event_type": "FOSS Meetup",
                "event_permalink": existing_permalink,
                "status": "Live",
                "event_start_date": datetime.now() + timedelta(days=4),
                "event_end_date": datetime.now() + timedelta(days=5),
                "event_description": fake.text(max_nb_chars=200),
            }
        )
        cross_chapter_event.insert()

        # Test 3: Same chapter, different slug (should succeed)
        different_slug_event = frappe.get_doc(
            {
                "doctype": EVENT,
                "chapter": original_chapter.name,
                "event_name": fake.text(max_nb_chars=40),
                "event_type": "FOSS Meetup",
                "event_permalink": fake.slug(),
                "status": "Live",
                "event_start_date": datetime.now() + timedelta(days=4),
                "event_end_date": datetime.now() + timedelta(days=5),
                "event_description": fake.text(max_nb_chars=200),
            }
        )
        different_slug_event.insert()

from datetime import datetime, timedelta

import frappe
from faker import Faker

from fossunited.doctype_ids import (
    CHAPTER,
    CITY_COMMUNITY,
    EVENT,
    EVENT_RSVP,
    EVENT_TICKET,
    HACKATHON,
    HACKATHON_LOCALHOST,
    HACKATHON_PARTICIPANT,
    HACKATHON_TEAM,
    JOIN_TEAM_REQUEST,
    RSVP_RESPONSE,
    USER_PROFILE,
)

fake = Faker()


def insert_test_chapter(**kwargs):
    """
    Generate a test chapter with flexible configuration options.

    Args:
        chapter_name (str, optional): Name of the chapter. Defaults to a random text.
        chapter_type (str, optional): Type of chapter. Defaults to CITY_COMMUNITY.
        city (str, optional): City of the chapter. Defaults to "Bangalore".
        state (str, optional): State of the chapter. Defaults to "Karnataka".
        lead_email (str, optional): Email of the chapter lead. Defaults to "test1@example.com".
        members (List[str], optional): List of member emails to add to the chapter.
        **kwargs : Any additional arguments, such as for social media links

    Returns:
        chapter doc: Created chapter document

    Raises:
        ValueError: If lead_email or member emails are invalid
        Exception: For any unexpected errors during chapter creation

    Example:
    ```
        chapter = insert_test_chapter(
            chapter_name="Python Developers Chapter",
            city="Mumbai",
            lead_email="lead@example.com",
            members=["member1@example.com", "member2@example.com"]
        )
    ```
    """
    try:
        # Validate and set default values
        chapter_data = {
            "doctype": CHAPTER,
            "chapter_name": kwargs.get("chapter_name", fake.text(max_nb_chars=40).strip()),
            "chapter_type": kwargs.get("chapter_type", CITY_COMMUNITY),
            "slug": kwargs.get("slug", fake.slug().replace("-", "_")),
            "city": kwargs.get("city", "Bangalore"),
            "state": kwargs.get("state", "Karnataka"),
            "country": "India",
            "email": kwargs.get("email", fake.email()),
            "facebook": kwargs.get("facebook", fake.url()),
            "instagram": kwargs.get("instagram", fake.url()),
            "linkedin": kwargs.get("linkedin", fake.url()),
            "mastodon": kwargs.get("mastodon", fake.url()),
            "matrix": kwargs.get("matrix", fake.url()),
            "x": kwargs.get("x", fake.url()),
        }

        # Create chapter document
        chapter = frappe.get_doc(chapter_data)
        chapter.insert()

        if not frappe.db.exists("Role", "Chapter Team Member"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Team Member"}).insert(
                ignore_permissions=True
            )
        if not frappe.db.exists("Role", "Chapter Lead"):
            frappe.get_doc({"doctype": "Role", "role_name": "Chapter Lead"}).insert(
                ignore_permissions=True
            )

        # Handle chapter lead
        lead_email = kwargs.get("lead_email", "test1@example.com")
        try:
            lead_profile = frappe.db.get_value(USER_PROFILE, {"user": lead_email}, "name")
        except frappe.DoesNotExistError:
            frappe.log_error(f"Lead profile not found for email: {lead_email}")
            raise ValueError(f"Invalid lead email: {lead_email}")

        # Add lead to chapter members
        chapter.append(
            "chapter_members",
            {
                "chapter_member": lead_profile,
                "role": "Lead",
            },
        )

        # Add additional members
        members = kwargs.get("members", [])
        for member in members:
            try:
                profile = frappe.db.get_value(USER_PROFILE, {"user": member}, "name")
                if not profile:
                    frappe.log_error(f"Profile not found for member: {member}")
                    continue  # Skip invalid members

                chapter.append(
                    "chapter_members",
                    {
                        "chapter_member": profile,
                        "role": "Core Team Member",
                    },
                )
            except Exception as member_error:
                frappe.log_error(f"Error processing member {member}: {str(member_error)}")

        # Save and reload chapter
        chapter.save()
        chapter.reload()

        return chapter

    except Exception:
        # Re-raise the exception to maintain original error handling
        raise


def insert_test_event(chapter: dict, **kwargs):
    """
    Generate a test event with flexible configuration options.

    Args:
        chapter (dict, optional): chapter to associate the event with.
                If not provided, a new test chapter will be generated.
        event_name (str, optional): Name of the event. Defaults to random text.
        event_type (str, optional): Type of event. Defaults to "FOSS Meetup".
        start_date (datetime, optional): Event start date. Defaults to today.
        end_date (datetime, optional): Event end date. Defaults to next day.
        status (str, optional): Event status. Defaults to "Live".

    Returns:
        event doc: Created event document

    Raises:
        ValueError: If chapter is invalid or event creation fails
        Exception: For any unexpected errors during event generation

    Example:
    ```
        event = insert_test_event(
            event_name="Python Developers Meetup",
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 6, 2),
            event_type="Conference"
        )
    ```
    """
    try:
        is_paid_event = kwargs.get("is_paid_event", 0)
        tiers = []
        if is_paid_event:
            tiers = kwargs.get(
                "tiers",
                [
                    {
                        "enabled": 1,
                        "title": "General",
                        "price": 100,
                    }
                ],
            )

        # Prepare event data with flexible defaults
        event_data = {
            "doctype": EVENT,
            "chapter": chapter.name,
            "event_name": kwargs.get("event_name", fake.text(max_nb_chars=20).strip()),
            "event_permalink": kwargs.get("event_permalink", fake.slug().replace("-", "_")),
            "status": kwargs.get("status", "Live"),
            "event_type": kwargs.get("event_type", "FOSS Meetup"),
            "event_start_date": kwargs.get("start_date", datetime.today() + timedelta(days=1)),
            "event_end_date": kwargs.get("end_date", datetime.today() + timedelta(days=2)),
            "event_description": kwargs.get(
                "description", f"Test event for {chapter.chapter_name}"
            ),
            "is_paid_event": is_paid_event,
            "tickets_status": kwargs.get("tickets_status", "Closed"),
            "tiers": tiers,
        }

        # Add any additional fields passed in kwargs
        for key, value in kwargs.items():
            if key not in event_data and key not in [
                "chapter",
                "event_name",
                "start_date",
                "end_date",
                "description",
            ]:
                event_data[key] = value

        # Create and insert event
        event = frappe.get_doc(event_data)
        event.insert()
        event.reload()

        return event

    except Exception:
        # Re-raise the exception to maintain original error handling
        raise


def insert_test_ticket(event: str, **kwargs):
    """
    Generate a test ticket linked to an event.

    Args:
        event: ID of linked event
    """
    ticket_data = {
        "doctype": EVENT_TICKET,
        "event": event,
        "is_transfer_ticket": kwargs.get("is_transfer_ticket", 0),
        "full_name": kwargs.get("full_name", fake.name()),
        "email": kwargs.get("email", fake.email()),
        "tier": kwargs.get("tier", "Test Tier"),
        "razorpay_payment": kwargs.get("razorpay_payment", ""),
        "wants_tshirt": kwargs.get("wants_tshirt", 0),
        "tshirt_size": kwargs.get("tshirt_size", "M"),
    }

    ticket = frappe.get_doc(ticket_data)
    ticket.flags.ignore_permissions = kwargs.get("ignore_permissions", False)
    ticket.insert()
    ticket.reload()

    return ticket


def insert_rsvp_form(event: str, **kwargs):
    """
    Generate a test RSVP form with flexible configuration options.

    Args:
        event (str or dict, optional): Linked event for the RSVP form.
                If not provided, a new test event will be generated.
        allow_edit (bool, optional): Whether RSVP can be edited. Defaults to True.
        requires_host_approval(bool, optional): Whether to accept all incoming RSVPs.
                Default: False.
        max_rsvp_count (int, optional): Maximum number of RSVPs. Defaults to 100.
        rsvp_description (str, optional): Description for the RSVP form.
        custom_questions (list, optional): List of custom questions for the RSVP form.
        **kwargs: Additional arguments to be passed to event generation if needed.

    Returns:
        rsvp doc: Created RSVP document

    Raises:
        ValueError: If event is invalid or RSVP creation fails
        Exception: For any unexpected errors during RSVP generation

    Example:
    ```
        rsvp = generate_test_rsvp(
            max_rsvp_count=50,
            rsvp_description="Annual Developer Meetup RSVP",
            custom_questions=[
                {"question": "What is your preferred programming language?", "type": "Data"}
            ]
        )
    ```
    """
    try:
        # If event is a dictionary, use its name, otherwise assume it's already a name
        event_name = event.name if hasattr(event, "name") else event

        # Prepare RSVP data with flexible defaults
        rsvp_data = {
            "doctype": EVENT_RSVP,
            "allow_edit": kwargs.get("allow_edit", 1),  # Default to allowing edits
            "event": event_name,
            "max_rsvp_count": kwargs.get("max_rsvp_count", 5),
            "requires_host_approval": kwargs.get("requires_host_approval", False),
            "rsvp_description": kwargs.get(
                "rsvp_description", fake.text(max_nb_chars=200).strip()
            ),
            "custom_questions": kwargs.get("custom_questions", []),
        }

        # Add any additional fields passed in kwargs
        for key, value in kwargs.items():
            if key not in rsvp_data and key not in ["event", "custom_questions"]:
                rsvp_data[key] = value

        # Create and insert RSVP
        rsvp = frappe.get_doc(rsvp_data)
        rsvp.insert()
        rsvp.reload()

        return rsvp

    except Exception as e:
        frappe.log_error(f"Error generating RSVP: {str(e)}")
        raise


def insert_rsvp_submission(linked_rsvp: str, **kwargs):
    """
        Generate a test RSVP submission with flexible configuration options.

    Args:
        linked_rsvp (str): The name of the RSVP form to link this submission to.
        submitted_by (str, optional): User who submitted the RSVP.
        name (str, optional): Name of the person submitting RSVP.
                               Defaults to a fake generated name.
        im_a (str, optional): Describes the submitter's background.
                               Defaults to "Professional".
        email (str, optional): Email of the submitter.
                               Defaults to a fake generated email.
        confirm_attendance (int, optional): Attendance confirmation status.
                                            Defaults to 1 (confirmed).
        custom_answers (list, optional): Answers to custom RSVP questions.
        **kwargs: Additional arguments to be passed to the RSVP submission.

    Returns:
        frappe.Document: Created RSVP submission document

    Raises:
        ValueError: If the linked RSVP form is invalid
        Exception: For any unexpected errors during submission generation

    """

    try:
        submission_data = {
            "doctype": RSVP_RESPONSE,
            "linked_rsvp": linked_rsvp,
            "submitted_by": kwargs.get("submitted_by", ""),
            "name1": kwargs.get("name", fake.name()),
            "im_a": kwargs.get("im_a", "Professional"),
            "email": kwargs.get("email", fake.email()),
            "status": kwargs.get("status", "Pending"),
            "confirm_attendance": kwargs.get("confirm_attendance", 1),
            "custom_answers": kwargs.get("custom_answers", []),
        }

        for key, value in kwargs.items():
            if key not in submission_data and key not in ["custom_answers"]:
                submission_data[key] = value

        submission = frappe.get_doc(submission_data)
        submission.insert()
        submission.reload()

        return submission

    except Exception:
        raise


def insert_test_hackathon(chapter: str, **kwargs):
    """
    Generate a test hackathon with flexible configuration options.

    Args:
        chapter (str): id of the linked chapter
        permalink (str, optional): Permalink of the hackathon. Defaults to random slug.
        hackathon_name (str, optional): Name of the hackathon. Defaults to random text.
        hackathon_type (str, optional): Type of the hackathon. Defaults to "Hybrid".
        start_date (datetime, optional): Hackathon start date. Defaults to tomorrow.
        end_date (datetime, optional): Hackathon end date. Defaults to day after tomorrow.
        hackathon_description(str, optional):Description of hackathon. Defaults to "Test Hackathon"
        **kwargs: Additional arguments to be passed to the hackathon document.

    Returns:
        hackathon doc: Created hackathon document

    Raises:
        Exception: For any unexpected errors during hackathon generation
    """
    hackathon_data = {
        "doctype": HACKATHON,
        "chapter": chapter,
        "permalink": kwargs.get("permalink", fake.slug().replace("-", "_")),
        "hackathon_name": kwargs.get("hackathon_name", fake.text(max_nb_chars=20).strip()),
        "hackathon_type": kwargs.get("hackathon_type", "Hybrid"),
        "start_date": kwargs.get("start_date", datetime.today() + timedelta(days=1)),
        "end_date": kwargs.get("end_date", datetime.today() + timedelta(days=2)),
        "hackathon_description": kwargs.get("hackathon_description", "Test Hackathon"),
    }

    for key, value in kwargs.items():
        if key not in hackathon_data:
            hackathon_data[key] = value

    hackathon = frappe.get_doc(hackathon_data)
    hackathon.insert()
    hackathon.reload()

    return hackathon


def insert_test_hackathon_team(hackathon: dict, **kwargs):
    """
    Generate a test hackathon team with flexible configuration options.

    Args:
        hackathon (dict): The hackathon to associate the team with.
        **kwargs: Additional arguments to be passed to the team document.

    Returns:
        team doc: Created hackathon team document

    Raises:
        Exception: For any unexpected errors during team generation
    """
    team_data = {
        "doctype": HACKATHON_TEAM,
        "hackathon": hackathon.get("name"),
        "team_name": kwargs.get("team_name", fake.name()),
    }

    for key, value in kwargs.items():
        if key not in team_data:
            team_data[key] = value

    team = frappe.get_doc(team_data)
    team.insert()
    team.reload()

    return team


def insert_test_hackathon_participant(hackathon_id: str, **kwargs):
    """
    Generate a test hackathon participant with flexible configuration options.

    Args:
        hackathon_id (str): The ID of the hackathon to link the participant to.
        full_name (str, optional): Full name of the participant. Defaults to a fake name.
        email (str, optional): Email of the participant. Defaults to a fake email.
        user (str, optional): User linked to the participant.
        **kwargs: Additional arguments to be passed to the participant document.

    Returns:
        participant doc: Created hackathon participant document

    Raises:
        Exception: For any unexpected errors during participant generation
    """
    participant_data = {
        "doctype": HACKATHON_PARTICIPANT,
        "full_name": kwargs.get("full_name", fake.name()),
        "email": kwargs.get("email", fake.email()),
        "hackathon": hackathon_id,
        "user": kwargs.get("user", ""),
    }

    for key, value in kwargs.items():
        if key not in participant_data:
            participant_data[key] = value

    participant = frappe.get_doc(participant_data)
    participant.insert()
    participant.reload()

    return participant


def insert_test_hackathon_join_request(
    hackathon_id: str, team_id: str, requested_by: str, reciever_email: str, **kwargs
):
    """
    Generate a test hackathon join request with flexible configuration options.
    Args:
        hackathon_id (str): The ID of the hackathon to link the join request to.
        team_id (str): The ID of the team to link the join request to.
        requested_by(str): The user id of the user sending the request.
        reciever_email (str): The email of the recipient of the join request.
        **kwargs: Additional arguments to be passed to the join request document.
    Returns:
        request doc: Created hackathon join request document
    Raises:
        Exception: For any unexpected errors during join request generation
    """
    request_data = {
        "doctype": JOIN_TEAM_REQUEST,
        "hackathon": hackathon_id,
        "team": team_id,
        "requested_by": requested_by,
        "reciever_email": reciever_email,
    }
    for key, value in kwargs.items():
        if key not in request_data:
            request_data[key] = value
    request = frappe.get_doc(request_data)
    request.insert()
    request.reload()
    return request


def insert_test_hackathon_localhost(parent_hackathon: str, **kwargs):
    """
    Generate a test hackathon localhost with flexible configuration options.
    Args:
        parent_hackathon (str): The ID of the hackathon to link the localhost to.
        **kwargs: Additional arguments to be passed to the localhost document.
    Returns:
        localhost doc: Created hackathon localhost document
    """
    localhost_data = {
        "doctype": HACKATHON_LOCALHOST,
        "parent_hackathon": parent_hackathon,
        "localhost_name": kwargs.get("localhost_name", fake.name()),
        "organizers": kwargs.get("organizers", []),
        "is_accepting_attendees": kwargs.get("is_accepting_attendees", 1),
    }

    localhost = frappe.get_doc(localhost_data)
    localhost.insert()
    localhost.reload()
    return localhost

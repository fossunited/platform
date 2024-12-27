from typing import Literal

import frappe

from fossunited.api.chapter import check_if_chapter_member
from fossunited.doctype_ids import CAMPAIGN, CHAPTER, EMAIL_GROUP, EMAIL_MEMBER, EVENT

EMAIL_GROUP_TYPES = Literal[
    "Chapter Main",
    "Event Participants",
    "CFP Proposers",
    "Accepted Proposers",
    "Rejected Proposers",
    "Other",
]


def create_email_group(
    type: EMAIL_GROUP_TYPES,
    reference_document: str,
    document_type: str = EVENT,
):
    """
    Create an email group linked to the event

    Args:
        type: type of email group
        reference_document: id of the reference document of type document_type
        document_type: type of reference document (default: "FOSS Chapter Event")
    """
    _doc = frappe.get_doc(document_type, reference_document)
    _chapter = _doc.get("chapter")

    if frappe.db.exists(
        EMAIL_GROUP,
        {
            "reference_document": reference_document,
            "document_type": document_type,
            "chapter": _chapter,
            "group_type": type,
        },
    ):
        raise frappe.ValidationError("Email Group already exists for this event")

    # This is done to prevent cases when event id and hackathon id are equal
    group_title = ""
    if document_type == EVENT:
        group_title = f"{type}-{reference_document}-Event"
    else:
        group_title = f"{type}-{reference_document}-Hackathon"

    _group_title = group_title[:140]
    group = frappe.get_doc(
        {
            "doctype": EMAIL_GROUP,
            "title": _group_title,
            "chapter": _chapter,
            "reference_document": reference_document,
            "document_type": document_type,
            "group_type": type,
        }
    )

    try:
        group.insert(ignore_permissions=True)
    except Exception as e:
        frappe.throw(f"Error while creating email group: {e}", frappe.ValidationError)

    group.reload()
    return group


def add_to_email_group(email_group: str, email: str):
    """
    Add an email to an email group

    Args:
        email_group: id of email group
        email: email to be added to the group
    """

    if not frappe.db.exists(EMAIL_GROUP, email_group):
        frappe.throw("This email group does not exist", frappe.DoesNotExistError)

    if frappe.db.exists(EMAIL_MEMBER, {"email_group": email_group, "email": email}):
        frappe.throw("Email already a part of this email group", frappe.DuplicateEntryError)

    member = frappe.get_doc({"doctype": EMAIL_MEMBER, "email_group": email_group, "email": email})
    member.insert(ignore_permissions=True)


@frappe.whitelist()
def create_newsletter_campaign(
    data: dict,
    reference_document: str = None,
    document_type: str = EVENT,
    chapter: str = None,
):
    """
    Create a newsletter document linked to the particular event / chapter

    Args:
        data(dict): data to be set in the doctype
        reference_document(str): if of the reference document of type `document_type`
        document_type(str): type of reference document linked. default: 'FOSS Chapter Event'
        chapter(str): id of chapter it is linked to
    """
    _reference_document = reference_document
    _chapter = chapter

    if not _reference_document and not _chapter:
        frappe.throw("Atleast one of reference_document or chapter is required")

    if not _chapter:
        # Get Chapter ID
        _chapter = frappe.db.get_value(document_type, _reference_document, ["chapter"])

    chapter_dict = frappe.db.get_value(
        CHAPTER,
        _chapter,
        ["name", "chapter_type", "chapter_name", "email"],
        as_dict=1,
    )

    if chapter_dict.chapter_type == "City Community":
        chapter_dict.chapter_name = f"FOSS United {chapter_dict.chapter_name}"
    if chapter_dict.chapter_type == "FOSS Club":
        chapter_dict.chapter_name = f"FOSS Club {chapter_dict.chapter_name}"

    recipient_groups = get_formatted_email_group(data.get("email_group"))
    attachments = get_formatted_attachment_list(data.get("attachments"))

    newsletter_doc = frappe.get_doc(
        {
            "doctype": "Newsletter",
            "document_type": document_type,
            "reference_document": reference_document,
            "chapter": chapter,
            "sender_name": chapter_dict.chapter_name,
            "sender_email": chapter_dict.email,
            "email_group": recipient_groups,
            "subject": data.get("subject"),
            "content_type": data.get("content_type"),
            "message": data.get("message"),
            "message_md": data.get("message_md"),
            "message_html": data.get("message_html"),
            "attachments": attachments,
        }
    )

    newsletter_doc.insert(ignore_permissions=True)
    newsletter_doc.reload()

    return newsletter_doc


@frappe.whitelist()
def get_newsletter_campaigns(
    reference_document: str = None, document_type: str = EVENT, chapter: str = None
):
    """
    Get all newsletter / email campaigns specific to an event or a chapter

    Args:
        reference_document: id of the document linked
        document_type: doctype of reference_document. default: FOSS Chapter Event
        chapter: id of the chapter

    Returns:
        list : of all the email campaigns
    """

    campaigns = frappe.db.get_all(
        doctype=CAMPAIGN,
        filters={
            "reference_document": reference_document,
            "document_type": document_type,
            "chapter": chapter,
        },
        fields=[
            "total_recipients",
            "total_views",
            "email_sent",
            "subject",
            "schedule_sending",
            "schedule_send",
            "name",
            "modified",
        ],
        order_by="modified desc",
        page_length=99,
    )

    for campaign in campaigns:
        status = ""

        if campaign.email_sent:
            status = "Sent"
        elif campaign.schedule_sending:
            status = "Scheduled"
        else:
            status = "Not Sent"

        campaign["status"] = status

    return campaigns


@frappe.whitelist()
def get_campaign_detail(id: str) -> dict:
    """
    Get campaign details and return it as dict

    args:
        id: campaign/newsletter id

    returns:
        dict: with details of the campaign/newsletter
    """

    campaign = frappe.db.get_value(CAMPAIGN, id, ["*"], as_dict=1)

    # transform attachments
    attachments = frappe.db.get_all(
        doctype="Newsletter Attachment",
        filters={"parent": campaign.name},
        page_length=999,
        fields=["*"],
    )
    _attachments = []
    for item in attachments:
        file = frappe.db.get_value(
            "File",
            {
                "file_url": item["attachment"],
            },
            ["*"],
            as_dict=1,
        )
        _attachments.append(file)

    # transform email groups
    email_groups = frappe.db.get_all(
        doctype="Newsletter Email Group",
        filters={
            "parent": campaign.name,
        },
        page_length=999,
        fields=["*"],
    )
    _email_groups = []
    for item in email_groups:
        group = frappe.db.get_value(
            EMAIL_GROUP,
            item.email_group,
            ["*"],
            as_dict=1,
        )
        _email_groups.append(
            {
                "label": group.group_type,
                "value": group.name,
                "description": f"{group.total_subscribers} subscribers",
            }
        )

    campaign["attachments"] = _attachments
    campaign["email_group"] = _email_groups

    return campaign


@frappe.whitelist()
def get_email_groups(
    reference_document: str = None,
    document_type: str = EVENT,
    chapter: str = None,
) -> list:
    """
    Get email group for a specific event or chapter

    Args:
        reference_document: id of the document linked
        document_type: doctype of reference_document. default: FOSS Chapter Event
        chapter: id of the chapter

    Returns:
        list : of all the emails groups
    """

    email_groups = frappe.db.get_all(
        EMAIL_GROUP,
        {
            "chapter": chapter,
            "reference_document": reference_document,
            "document_type": document_type,
        },
        ["total_subscribers", "group_type", "name"],
    )

    return email_groups


@frappe.whitelist()
def update_campaign(campaign_id: str, data: dict):
    """
    Update an email campaign with new details(data)

    Args:
        campaign_id: campaign id
        data: updated data
    """

    campaign = frappe.get_doc(CAMPAIGN, campaign_id)

    for key, val in data.items():
        if key == "status":
            continue
        if getattr(campaign, key) == val:
            continue
        if key == "attachments":
            campaign.set(key, get_formatted_attachment_list(val))
        elif key == "email_group":
            campaign.set(key, get_formatted_email_group(val))
        else:
            campaign.set(key, val)

    campaign.save(ignore_permissions=True)


def get_formatted_email_group(groups: list) -> list:
    """
    Format the email group coming from frontend to backend compatible version

    oncoming:
    [
        {
            'label': 'Label XYZ',
            'value': 'xyz',
            'description': 'text',
        }
    ]

    format to:
    [
        {
            'email_group': value (from incoming),
        }
    ]

    args:
        groups: list of email groups

    returns:
        list: of formatted email groups
    """
    formatted_groups = []

    for group in groups:
        formatted_groups.append({"email_group": group.get("value")})

    return formatted_groups


def get_formatted_attachment_list(attachments: list) -> list:
    """
    Format a list of attachments coming from frontend to backend compatible version

    oncoming:
    [
        {
            file_name: '...',
            file_url: '...',
            type: '...',
            ...,
        }
    ]

    format to:
    [
        {
            attachment: file_url,
        }
    ]

    args:
        attachments: list of attachments

    returns:
        list: of formatted attachments
    """

    formatted_attachments = []

    for attachment in attachments:
        formatted_attachments.append({"attachment": attachment.get("file_url")})

    return formatted_attachments


@frappe.whitelist()
def send_campaign(campaign_id: str):
    """
    Send the campaigns

    args:
        campaign: id of campaign / newsletter doctype
    """
    campaign = frappe.get_doc(CAMPAIGN, campaign_id)

    if not campaign.chapter:
        chapter = frappe.db.get_value(EVENT, campaign.event, ["chapter"])
    else:
        chapter = campaign.chapter

    if not check_if_chapter_member(chapter, frappe.session.user):
        frappe.throw("You are not authorised for this action", frappe.PermissionError)

    campaign.flags.ignore_permissions = 1
    campaign.send_emails()
    campaign.save()


@frappe.whitelist()
def send_test_email(campaign_id: str, email: str):
    """
    Send out a test email for a campaign

    args:
        campaign_id : campaign / newsletter id
        email: email to send test email to
    """

    campaign = frappe.get_doc(CAMPAIGN, campaign_id)

    if not campaign.chapter:
        chapter = frappe.db.get_value(
            campaign.document_type,
            campaign.reference_document,
            ["chapter"],
        )
    else:
        chapter = campaign.chapter

    if not check_if_chapter_member(chapter, frappe.session.user):
        frappe.throw("You are not authorised for this action", frappe.PermissionError)

    campaign.flags.ignore_permissions = 1
    try:
        campaign.send_test_email(email)
        campaign.save()
    except frappe.InvalidEmailAddressError as e:
        frappe.throw(str(e))


@frappe.whitelist()
def get_sending_status(campaign_id: str) -> dict:
    """
    Get sending stats related to a campaign

    args:
        campaign_id: id of campaign for which stats are required

    returns:
        dict: of stats of format
        ```
        {
            'sent': int,
            'error': int,
            'total': int,
            'emails_queued': int,
        }
        ```
    """

    campaign = frappe.get_doc(CAMPAIGN, campaign_id)

    if not campaign.chapter:
        chapter = frappe.db.get_value(
            campaign.document_type,
            campaign.reference_document,
            ["chapter"],
        )
    else:
        chapter = campaign.chapter

    if not check_if_chapter_member(chapter, frappe.session.user):
        frappe.throw("You are not authorised for this action", frappe.PermissionError)

    campaign.flags.ignore_permissions = 1

    stats = campaign.get_sending_status()

    return stats

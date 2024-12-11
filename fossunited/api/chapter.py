import frappe

from fossunited.doctype_ids import CHAPTER, USER_PROFILE


@frappe.whitelist(allow_guest=True)
def check_if_chapter_member(chapter: str, user: str = frappe.session.user) -> bool:
    """
    Check if the user is a member of the chapter.

    Args:
        chapter (str): Chapter id
        user (str): User email. Default is current user.

    Returns:
        bool: True if the user is a member of the chapter, False otherwise.
    """
    profile = frappe.db.get_value(USER_PROFILE, {"user": user}, ["name"])

    if not profile:
        return False

    is_member = bool(
        frappe.db.exists(
            "FOSS Chapter Lead Team Member",
            {
                "parent": chapter,
                "parenttype": CHAPTER,
                "chapter_member": profile,
                "parentfield": "chapter_members",
            },
        )
    )

    return is_member

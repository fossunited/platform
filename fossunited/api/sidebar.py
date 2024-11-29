import frappe


@frappe.whitelist(allow_guest=True)
def get_sidebar_items(user: str = frappe.session.user):
    sidebar_items = [
        {
            "parent_label": "Profile",
            "items": [
                {
                    "label": "Details",
                    "route": "/me",
                },
                {"label": "My Proposals", "route": "/my-proposals"},
            ],
        },
        {
            "parent_label": "Hackathons",
            "items": [
                {
                    "label": "Hackathons",
                    "route": "/my-hackathons",
                },
            ],
        },
    ]

    if user_is_chapter_member(user):
        sidebar_items.append(
            {
                "parent_label": "Organizer Dashboard",
                "items": [
                    {
                        "label": "Manage Chapter",
                        "route": "/chapter",
                    },
                ],
            }
        )

    if user_is_localhost_organizer(user):
        sidebar_items[1]["items"].append(
            {
                "label": "Manage Localhost",
                "route": "/localhost",
            }
        )

    if user_is_cfp_reviewer(user):
        sidebar_items.append(
            {
                "parent_label": "CFP Reviewer",
                "items": [
                    {
                        "label": "Review Proposals",
                        "route": "/review",
                    },
                ],
            }
        )

    return sidebar_items


def user_is_chapter_member(user: str = frappe.session.user):
    return bool(
        frappe.db.exists(
            "Has Role",
            {"role": "Chapter Team Member", "parent": user},
        )
    )


def user_is_localhost_organizer(user: str = frappe.session.user):
    return bool(
        frappe.db.exists(
            "Has Role",
            {"role": "Localhost Organizer", "parent": user},
        )
    )


def user_is_cfp_reviewer(user: str = frappe.session.user):
    return bool(
        frappe.db.exists(
            "Has Role",
            {"role": "CFP Reviewer", "parent": user},
        )
    )

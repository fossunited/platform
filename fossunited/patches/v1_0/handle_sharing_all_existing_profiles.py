import frappe

from fossunited.doctype_ids import USER_PROFILE


def execute():
    """
    In this patch, all the existing profiles will be shared with their own user.
    And these users will be given "Read", "Write" and "Share" perms to their profiles.
    """
    profiles = frappe.db.get_all(USER_PROFILE, ["name", "user"], page_length=99999)

    for p in profiles:
        share_doc = frappe.get_doc(
            {
                "doctype": "DocShare",
                "user": p.user,
                "share_doctype": USER_PROFILE,
                "share_name": p.name,
                "read": 1,
                "write": 1,
                "share": 1,
            }
        )
        try:
            share_doc.insert()
        except Exception as e:
            frappe.log_error(f"Error while sharing profile for profile: {p.name}", str(e))
            continue

import io

import frappe
from frappe.utils.file_manager import save_file
from PIL import Image

from fossunited.api.dashboard import get_session_user_profile
from fossunited.doctype_ids import CHAPTER, RESTRICTED_USERNAME, USER_PROFILE


def convert_image_to_webp(image_content: bytes) -> bytes:
    """
    Convert the given image content to WebP format using Pillow.
    Returns the converted image as bytes.
    """
    try:
        with Image.open(io.BytesIO(image_content)) as img:
            img = img.convert("RGB")
            webp_io = io.BytesIO()
            img.save(webp_io, format="WEBP", quality=80)
            return webp_io.getvalue()
    except Exception as e:
        frappe.throw(f"Failed to process image: {str(e)}")


@frappe.whitelist()
def set_profile_image(file_url: str) -> bool:
    """
    Download the image from file_url, convert it to WebP, save it using Frappe's file handling,
    and update the user's profile image.
    """
    user_doc = get_session_user_profile()
    try:
        file_path = frappe.get_site_path("public", file_url.lstrip("/"))
        with open(file_path, "rb") as f:
            original_image = f.read()

        webp_image = convert_image_to_webp(original_image)
        filename = f"profile_{user_doc.name}.webp"

        saved_file = save_file(
            fname=filename, content=webp_image, dt=USER_PROFILE, dn=user_doc.name, is_private=False
        )

        frappe.db.set_value(USER_PROFILE, user_doc.name, "profile_photo", saved_file.file_url)
        frappe.db.set_value("User", frappe.session.user, "user_image", saved_file.file_url)
        return True

    except Exception as e:
        frappe.throw(str(e))


@frappe.whitelist()
def set_cover_image(file_url: str) -> bool:
    """
    Download the image from file_url, convert it to WebP, save it using Frappe's file handling,
    and update the cover image in the user's profile.
    """
    user_doc = get_session_user_profile()
    try:
        file_path = frappe.get_site_path("public", file_url.lstrip("/"))
        with open(file_path, "rb") as f:
            original_image = f.read()

        webp_image = convert_image_to_webp(original_image)
        filename = f"cover_{user_doc.name}.webp"

        saved_file = save_file(
            fname=filename, content=webp_image, dt=USER_PROFILE, dn=user_doc.name, is_private=False
        )

        frappe.db.set_value(USER_PROFILE, user_doc.name, "cover_image", saved_file.file_url)
        return True

    except Exception as e:
        frappe.throw(str(e))


@frappe.whitelist()
def toggle_profile_privacy(value):
    user_doc = get_session_user_profile()
    try:
        frappe.db.set_value(USER_PROFILE, user_doc.name, "is_private", value)
        return True
    except Exception as e:
        frappe.throw(str(e))


@frappe.whitelist()
def update_profile(fields_dict):
    """
    Updates User Profile data.
    Combined with Full Name and Username updates in User doctype,
    whenever these fields are updated.
    """
    user_doc = get_session_user_profile()
    try:
        updated_fields = {
            "full_name": fields_dict.get("full_name"),
            "username": fields_dict.get("username"),
            "bio": fields_dict.get("bio"),
            "current_city": fields_dict.get("current_city"),
            "about": fields_dict.get("about"),
            "website": fields_dict.get("website"),
            "x": fields_dict.get("x"),
            "linkedin": fields_dict.get("linkedin"),
            "github": fields_dict.get("github"),
            "gitlab": fields_dict.get("gitlab"),
            "instagram": fields_dict.get("instagram"),
            "youtube": fields_dict.get("youtube"),
            "devto": fields_dict.get("devto"),
            "medium": fields_dict.get("medium"),
            "mastodon": fields_dict.get("mastodon"),
        }

        profile = frappe.get_doc(USER_PROFILE, user_doc.name)
        for field, value in updated_fields.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        profile.save(ignore_permissions=True)

        user_updates = {}
        if fields_dict.get("full_name") != user_doc.full_name:
            name_parts = fields_dict.get("full_name").split()
            if len(name_parts) > 1:
                user_updates["first_name"] = name_parts[0]
                user_updates["last_name"] = "".join(name_parts[1:])
            else:
                user_updates["first_name"] = name_parts[0]
                user_updates["last_name"] = ""

        if fields_dict.get("username") != user_doc.username:
            user_updates["username"] = fields_dict.get("username")

        if user_updates:
            user = frappe.get_doc("User", user_doc.user)
            for field, value in user_updates.items():
                setattr(user, field, value)

            user.save(ignore_permissions=True)

        return True

    except Exception as e:
        frappe.log_error(("Error updating profile: {0}").format(str(e)))
        frappe.throw(("An error occurred while updating the profile. Please try again."))


@frappe.whitelist()
def is_valid_username(username: str, id: str) -> bool:
    """
    Check if the username is unique and not in restricted list

    Args:
        username: Username to check
        id: ID of the user profile

    Returns:
        bool: True if username is unique and not a restricted username
    """
    if (
        frappe.db.exists(CHAPTER, {"route": username})
        or frappe.db.exists(
            USER_PROFILE,
            {"route": username, "name": ["!=", id]},
        )
        or frappe.db.exists(
            RESTRICTED_USERNAME,
            {
                "username": username,
            },
        )
    ):
        return False

    return True

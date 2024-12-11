from datetime import datetime

import frappe

from fossunited.doctype_ids import EVENT


def conclude_events():
    """
    Get all the events which have ended (end_date < today) and set their status to concluded
    """
    events = frappe.db.get_all(
        EVENT,
        {"status": "Live", "event_end_date": ["<", datetime.today()]},
        ["name", "status", "event_end_date", "event_start_date"],
        page_length=999,
    )

    for event in events:
        doc = frappe.get_doc(EVENT, event.name)
        doc.status = "Concluded"
        try:
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(
                frappe.get_traceback(),
                f"Error while concluding events through scheduler- ID:{doc.name}\nError:{str(e)}",
            )
            continue

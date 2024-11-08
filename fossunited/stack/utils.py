from collections import defaultdict

import frappe


def get_stack_dict():
    stacks = frappe.get_all(doctype="Stack", fields=["name1", "icon", "category"], page_length=999)

    stack_dict = defaultdict(list)

    for item in stacks:
        stack_dict[item.category].append(item)

    return dict(stack_dict)

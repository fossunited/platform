import frappe


def get_stack_dict():
    stacks = frappe.get_all(doctype="Stack", fields=["name1", "icon", "category"], page_length=999)

    stack_dict = {}

    for item in stacks:
        if item.category not in stack_dict:
            stack_dict.update({item.category: []})

        stack_dict[item.category].append(item)

    return stack_dict

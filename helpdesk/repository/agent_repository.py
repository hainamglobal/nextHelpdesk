import frappe


def check_name_is_exist(name):
    if frappe.db.exists("HD Agent",name):
        return True
    else:
        return False

def delete_agent_repository(name):
    agent_repository = frappe.get_doc("HD Agent", name)
    # Xóa document
    agent_repository.delete()
    frappe.db.commit()



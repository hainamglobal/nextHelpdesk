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

class AgentRepository:
    def search_emails(self, query: str):
        # Truy vấn danh sách email từ bảng User có chứa chuỗi query
        sql = """
            SELECT email, full_name, user_image
            FROM `tabUser`
            WHERE email LIKE %s AND enabled = 1
            LIMIT 20
        """
        return frappe.db.sql(sql, f"%{query}%", as_dict=True)

import frappe


def check_name_is_exist(name):
    if frappe.db.exists("HD Agent",name):
        return True
    else:
        return False

def delete_agent_repository(name):
    agent_repository = frappe.get_doc("HD Agent", name)
    agent_repository.delete()

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

    def get_agent_for_assignment(self):
        """
        Thuật toán:
        1. Ưu tiên người ít phiếu (HD Ticket) đang Open nhất
        2. Nếu bằng nhau -> Round Robin (chọn người có thời gian được gán phiếu xa nhất / cũ nhất)
        """
        sql = """
            SELECT 
                a.user,
                SUM(CASE WHEN todo.status = 'Open' THEN 1 ELSE 0 END) as open_tickets,
                MAX(todo.creation) as last_assigned
            FROM 
                `tabHD Agent` a
            LEFT JOIN 
                `tabToDo` todo ON todo.allocated_to = a.user AND todo.reference_type = 'HD Ticket'
            WHERE 
                a.is_active = 1
            GROUP BY 
                a.user
            ORDER BY 
                open_tickets ASC, 
                last_assigned ASC
            LIMIT 1
        """
        result = frappe.db.sql(sql, as_dict=True)
        if result:
            return result[0].get("user")
        return None

    def get_open_tickets_by_agent(self, email: str):
        sql = """
            SELECT reference_name 
            FROM `tabToDo`
            WHERE reference_type = 'HD Ticket' 
              AND allocated_to = %s 
              AND status = 'Open'
        """
        return [row.reference_name for row in frappe.db.sql(sql, email, as_dict=True)]

    def reassign_ticket(self, ticket_name: str, old_agent_email: str, new_agent_email: str):
        from frappe.desk.form.assign_to import add as assign_to_add, remove as assign_to_remove

        # Xóa gán cũ
        assign_to_remove("HD Ticket", ticket_name, old_agent_email)

        # Thêm gán mới
        assign_to_add({
            "assign_to": [new_agent_email],
            "doctype": "HD Ticket",
            "name": ticket_name,
            "description": "Hệ thống tự động phân công lại do Agent cũ bị xóa"
        })

    def delete_orphaned_todo(self, ticket_name: str):
        # Xóa các ToDo rác nếu phiếu thực tế không còn tồn tại
        frappe.db.sql("DELETE FROM `tabToDo` WHERE reference_type='HD Ticket' AND reference_name=%s", ticket_name)

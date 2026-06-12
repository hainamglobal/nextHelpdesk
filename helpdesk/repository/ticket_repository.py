import frappe

class TicketRepository:
    def get_ticket_info(self, ticket_name: str) -> dict:
        """
        Lấy thông tin cơ bản của ticket bao gồm mã phiếu, tiêu đề, người tạo
        """
        if not frappe.db.exists("HD Ticket", ticket_name):
            return None
            
        ticket = frappe.get_doc("HD Ticket", ticket_name)
        
        # Thử lấy tên đầy đủ của người tạo từ bảng User
        raised_by_email = ticket.raised_by
        raised_by_name = frappe.db.get_value("User", {"email": raised_by_email}, "full_name")
        
        if not raised_by_name:
            raised_by_name = raised_by_email
            
        return {
            "name": ticket.name,
            "subject": ticket.subject,
            "raised_by": raised_by_email,
            "raised_by_name": raised_by_name
        }

import frappe
from helpdesk.config.response.error_code import ErrorConfig
from helpdesk.config.response import CommonException
from helpdesk.repository.agent_repository import delete_agent_repository, check_name_is_exist, AgentRepository
from helpdesk.service.external_channel_service import HDRavenChannelService


class AgentService:
    def __init__(self):
        self.raven_service = HDRavenChannelService()
        self.agent_repo = AgentRepository()

    def get_list_email(self, query: str):
        query = query.strip() if query else ""
        return self.agent_repo.search_emails(query)

    def delete_agent(self, name):
        if "System Manager" not in frappe.get_roles(frappe.session.user):
            raise CommonException(ErrorConfig.FORBIDDEN_ERROR)

        check = check_name_is_exist(name)
        if check:
            try:
                email = frappe.db.get_value("HD Agent", name, "user")
                if email:
                    try:
                        self.raven_service.delete_user_in_channel(email)
                    except Exception as e:
                        frappe.log_error(title="Delete Raven Channel Member Error", message=str(e))
                
                # Lấy danh sách phiếu đang mở của Agent này trước khi xóa
                open_tickets = self.agent_repo.get_open_tickets_by_agent(email) if email else []

                # Xóa Agent
                delete_agent_repository(name)
                
                # Tự động gán lại các phiếu đang mở
                if open_tickets and email:
                    self.reassign_tickets_from_deleted_agent(email, open_tickets)
            except Exception as e:
                frappe.db.rollback()
                raise e
            
            return True
        else:
            raise CommonException(ErrorConfig.AGENT_NOT_EXIST)

    def reassign_tickets_from_deleted_agent(self, old_agent_email: str, open_tickets: list):
        old_agent_name = frappe.db.get_value("User", {"email": old_agent_email}, "full_name") or old_agent_email

        for ticket_name in open_tickets:
            try:
                new_agent_email = self.auto_assign_agent()
                if new_agent_email and old_agent_email:
                    self.agent_repo.reassign_ticket(ticket_name, old_agent_email, new_agent_email)

                    # Gửi thông báo chuyển phiếu vào nhóm Raven
                    try:
                        new_agent_name = frappe.db.get_value("User", {"email": new_agent_email}, "full_name") or new_agent_email
                        subject = frappe.db.get_value("HD Ticket", ticket_name, "subject") or ticket_name
                        self.raven_service.send_reassign_notification(
                            ticket_name=ticket_name,
                            subject=subject,
                            old_agent_email=old_agent_email,
                            old_agent_name=old_agent_name,
                            new_agent_email=new_agent_email,
                            new_agent_name=new_agent_name
                        )
                    except Exception as e:
                        frappe.log_error(title="Raven Reassign Notify Error", message=str(e))

            except frappe.DoesNotExistError:
                self.agent_repo.delete_orphaned_todo(ticket_name)
            except CommonException:
                break

    def auto_assign_agent(self):
        agent_user = self.agent_repo.get_agent_for_assignment()
        if not agent_user:
            ErrorConfig.AT_LEAST_ONE_AGENT.throw()
        return agent_user





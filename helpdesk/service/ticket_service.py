import frappe
from helpdesk.repository.ticket_repository import TicketRepository
from helpdesk.service.external_channel_service import RavenChannelService
from helpdesk.config.response.error_code import ErrorConfig
from helpdesk.config.response.common_exception import CommonException

class TicketService:
    def __init__(self):
        self.ticket_repo = TicketRepository()
        self.raven_service = RavenChannelService()
        
    def notify_raven_new_ticket(self, ticket_name: str):
        """
        Gọi API gửi thông tin phiếu hỗ trợ vừa tạo vào nhóm Raven
        """
        ticket_info = self.ticket_repo.get_ticket_info(ticket_name)
        if not ticket_info:
            raise CommonException(ErrorConfig.TICKET_NOT_EXIST)
            
        raised_by_email = ticket_info.get("raised_by")
        raised_by_name = ticket_info.get("raised_by_name")
        
        # Gửi notification qua RavenChannelService
        result = self.raven_service.send_ticket_notification(
            ticket_name=ticket_info.get("name"),
            subject=ticket_info.get("subject"),
            raised_by_email=raised_by_email,
            raised_by_name=raised_by_name
        )
        
        return result

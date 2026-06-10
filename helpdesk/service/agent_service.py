import frappe
from helpdesk.config.response.error_code import ErrorConfig
from helpdesk.config.response import CommonException
from helpdesk.repository.agent_repository import delete_agent_repository, check_name_is_exist, AgentRepository
from helpdesk.service.external_channel_service import RavenChannelService


class AgentService:
    def __init__(self):
        self.raven_service = RavenChannelService()
        self.agent_repo = AgentRepository()

    def get_list_email(self, query: str):
        query = query.strip() if query else ""
        return self.agent_repo.search_emails(query)

    def delete_agent(self, name):
        if "System Manager" not in frappe.get_roles(frappe.session.user):
            raise CommonException(ErrorConfig.FORBIDDEN_ERROR)

        check = check_name_is_exist(name)
        if check:
            email = frappe.db.get_value("HD Agent", name, "user")
            if email:
                try:
                    self.raven_service.delete_user_in_channel(email)
                except Exception as e:
                    frappe.log_error(title="Delete Raven Channel Member Error", message=str(e))
            delete_agent_repository(name)
            return True
        else:
            raise CommonException(ErrorConfig.AGENT_NOT_EXIST)





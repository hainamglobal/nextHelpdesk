import frappe
from helpdesk.config.error_config import ErrorConfig
from helpdesk.repository.agent_repository import delete_agent_repository, check_name_is_exist
from helpdesk.service.external_channel_service import RavenChannelService


class AgentService:
    def __init__(self):
        self.raven_service = RavenChannelService()

    def delete_agent(self, name):
        frappe.only_for("System Manager")

        check = check_name_is_exist(name)
        if check:
            email = frappe.db.get_value("HD Agent", name, "user")
            if email:
                try:
                    self.raven_service.delete_user_in_channel(email)
                except Exception as e:
                    frappe.log_error(title="Delete Raven Channel Member Error", message=str(e))

            delete_agent_repository(name)
        else:
            frappe.throw(ErrorConfig.AGENT_NOT_EXIST.message)





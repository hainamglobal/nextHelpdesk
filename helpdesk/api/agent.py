import frappe
from helpdesk.service.agent_service import AgentService
from helpdesk.service.external_channel_service import RavenChannelService
from helpdesk.config.response import DefaultRes, ResponseMessage, CommonException
from helpdesk.config.response.error_code import ErrorConfig


@frappe.whitelist()
def sent_invites(emails, send_welcome_mail_to_user=True):
    created_agents = []
    try:
        channel_service = RavenChannelService()
        
        for email in emails:
            if frappe.db.exists("User", email):
                user = frappe.get_doc("User", email)
            else:
                user = frappe.get_doc(
                    {"doctype": "User", "email": email, "first_name": email.split("@")[0]}
                ).insert()

                if send_welcome_mail_to_user:
                    user.send_welcome_mail_to_user()

            # Thêm user vào channel qua service
            res = channel_service.add_user_to_chanel_site_config(email)
            channel_id = res.get("channel_id")
            # Tạo HD Agent
            doc = {"doctype": "HD Agent", "user": user.name , "channel_id": channel_id}
            new_agent = frappe.get_doc(doc).insert()
            created_agents.append(new_agent.as_dict())
            return DefaultRes.res(200, ResponseMessage.SUCCESS, created_agents).to_dict()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("Lỗi sent_invites (HD Agent)", frappe.get_traceback())
        raise CommonException(ErrorConfig.CREATE_AGENT_ERROR.throw(str(e)))

@frappe.whitelist()
def delete_agent(name):
        agent_service = AgentService()
        return DefaultRes.res(200, ResponseMessage.SUCCESS,agent_service.delete_agent(name)).to_dict()

@frappe.whitelist()
def get_list_email(query=""):
    agent_service = AgentService()
    result = agent_service.get_list_email(query)
    return DefaultRes.res(200, ResponseMessage.SUCCESS, result).to_dict()

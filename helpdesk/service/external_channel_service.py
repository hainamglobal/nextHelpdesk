import frappe
from functools import wraps
from helpdesk.config.response.error_code import ErrorConfig
from helpdesk.config.response.common_exception import CommonException
from helpdesk.repository.hd_agent_channel_repository import insert_chanel_id, count_channel_id, get_channel_id

def run_as_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        original_user = getattr(frappe.session, "user", "Guest")
        try:
            frappe.set_user("adminhotro@gmail.com")
            return func(*args, **kwargs)
        finally:
            frappe.set_user(original_user)
    return wrapper

class HDRavenChannelService:
    def __init__(self):
        self.channel_name = "Nhóm hỗ trợ khách hàng nextGRP"
        
        channel_id = self.check_local_channel()
        if not channel_id:
            channel_id = self.create_raven_channel()
            self.insert_channel_agent_name(channel_id)
            
        self.channel_id = channel_id

        if not self.get_member_from_email("adminhotro@gmail.com"):
            self.add_member_to_channel("adminhotro@gmail.com")

    @run_as_admin
    def create_raven_channel(self):
        try:
            doc = frappe.get_doc({
                "doctype": "Raven Channel",
                "channel_name": self.channel_name,
                "workspace": "Raven"
            })
            doc.insert(ignore_permissions=True)
            return doc.name

        except Exception as e:
            frappe.log_error(title=ErrorConfig.CREATE_CHANNEL_LOG_TITLE.message, message=str(e))
            frappe.throw(ErrorConfig.CREATE_CHANNEL_THROW.message)

    @run_as_admin
    def add_member_to_channel(self, member_email):
        try:
            import raven.api.raven_channel_member
            raven.api.raven_channel_member.add_channel_members(
                channel_id=self.channel_id,
                members=[member_email]
            )
            return True

        except Exception as e:
            frappe.log_error(title=ErrorConfig.ADD_MEMBER_LOG_TITLE.message, message=str(e))
            frappe.throw(ErrorConfig.ADD_MEMBER_THROW.message)

    @run_as_admin
    def _check_channel_is_exist(self):
        try:
            import raven.api.check_channel_is_exist
            res = raven.api.check_channel_is_exist.check_channel_is_exist(channel_id=self.channel_id)
            return res
        except Exception as e:
            frappe.throw(str(e))
    @run_as_admin
    def get_member_from_email(self, email):
        try:
            import raven.api.raven_channel_member
            res = raven.api.raven_channel_member.get_member_from_email(email=email, channel_id=self.channel_id)
            return res.get("member_id") if isinstance(res, dict) else ""
        except Exception as e:
            frappe.throw(str(e))

    @run_as_admin
    def delete_user_in_channel(self, email):
        member_id = self.get_member_from_email(email)
        if not member_id:
            frappe.throw("Không tìm thấy member_id từ email")
    
        try:
            import raven.api.raven_channel_member
            raven.api.raven_channel_member.delete_channel_member(
                channel_id=self.channel_id,
                member_id=member_id
            )
            return True
        except Exception as e:
            frappe.throw(str(e))

    @run_as_admin
    def send_ticket_notification(self, ticket_name, subject, assigned_email, assigned_name):
        site_url = frappe.utils.get_url()
        ticket_link = f"{site_url}/helpdesk/tickets/{ticket_name}"
        
        if assigned_email:
            handler_text = f"""<span data-type="userMention" class="mention" data-id="{assigned_email}" data-label="{assigned_name}">@{assigned_name}</span>"""
        else:
            handler_text = f"""<strong>{assigned_name}</strong>"""
            
        text = f"""<div style="border:1px solid #d1d5db;border-radius:12px;padding:16px;background:#ffffff;max-width:450px;font-family:Arial,sans-serif;"><div style="font-size:18px;font-weight:bold;color:#2563eb;margin-bottom:8px;">🎫 Phiếu hỗ trợ mới</div><div style="margin-bottom:8px;"><strong>Mã phiếu:</strong> {ticket_name}</div><div style="margin-bottom:8px;"><strong>Tiêu đề:</strong> {subject}</div><div style="margin-bottom:16px;"><strong>Người xử lý phiếu:</strong> {handler_text}</div><a href="{ticket_link}" target="_blank" style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;padding:10px 16px;border-radius:8px;font-weight:600;">Xem chi tiết phiếu hỗ trợ</a></div>"""

        try:
            import raven.api.raven_message
            raven.api.raven_message.send_message(
                channel_id=self.channel_id,
                text=text,
                is_reply=False,
                send_silently=False
            )
            return True
        except Exception as e:
            frappe.log_error(title=ErrorConfig.SEND_MESSAGE_LOG_TITLE.message, message=str(e))
            raise CommonException(ErrorConfig.SEND_MESSAGE_THROW)

    @run_as_admin
    def send_reassign_notification(self, ticket_name, subject, old_agent_email, old_agent_name, new_agent_email, new_agent_name):
        site_url = frappe.utils.get_url()
        ticket_link = f"{site_url}/helpdesk/tickets/{ticket_name}"

        if new_agent_email:
            new_handler = f"""<span data-type="userMention" class="mention" data-id="{new_agent_email}" data-label="{new_agent_name}">@{new_agent_name}</span>"""
        else:
            new_handler = f"""<strong>{new_agent_name}</strong>"""

        text = f"""<div style="border:1px solid #fbbf24;border-radius:12px;padding:16px;background:#fffbeb;max-width:450px;font-family:Arial,sans-serif;"><div style="font-size:18px;font-weight:bold;color:#d97706;margin-bottom:8px;">🔄 Chuyển phiếu hỗ trợ</div><div style="margin-bottom:8px;"><strong>Mã phiếu:</strong> {ticket_name}</div><div style="margin-bottom:8px;"><strong>Tiêu đề:</strong> {subject}</div><div style="margin-bottom:8px;"><strong>Agent cũ:</strong> {old_agent_name} (đã bị xóa)</div><div style="margin-bottom:16px;"><strong>Người xử lý mới:</strong> {new_handler}</div><a href="{ticket_link}" target="_blank" style="display:inline-block;background:#d97706;color:#ffffff;text-decoration:none;padding:10px 16px;border-radius:8px;font-weight:600;">Xem chi tiết phiếu</a></div>"""

        try:
            import raven.api.raven_message
            raven.api.raven_message.send_message(
                channel_id=self.channel_id,
                text=text,
                is_reply=False,
                send_silently=False
            )
            return True
        except Exception as e:
            frappe.log_error(title="Raven Reassign Notification Error", message=str(e))


    def check_local_channel(self):
        if count_channel_id(self.channel_name) > 1 :
            raise CommonException(ErrorConfig.CHANNEL_IS_EXIST)
        else:
            channel_id = get_channel_id(self.channel_name)
            # Kiểm tra xem channel có thực sự tồn tại trong hệ thống Raven không (phòng trường hợp đã bị xóa tay)
            if channel_id and not frappe.db.exists("Raven Channel", channel_id):
                frappe.db.delete("HD Channel Agent", {"channel_agent_name": self.channel_name})
                return None
            return channel_id


    def insert_channel_agent_name(self, channel_id):
        insert_chanel_id(channel_id, self.channel_name)

    def add_user_to_chanel_site_config(self, member_email):
        self.add_member_to_channel(member_email)

        return {
            "status": "success",
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "members_added": [member_email]
        }
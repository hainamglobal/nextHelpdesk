import frappe
import requests
from helpdesk.config.config_sites import get_nextgrp_develop_config
from helpdesk.config.response.error_code import ErrorConfig
from helpdesk.config.response.common_exception import CommonException
from helpdesk.repository.hd_agent_channel_repository import insert_chanel_id


class RavenChannelService:
    def __init__(self):
        self.config = get_nextgrp_develop_config()
        self.channel_name = "Nhóm hỗ trợ khách hàng nextGrp"
        
        channel_id = self.check_local_channel()
        if not channel_id:
            channel_id = self.create_raven_channel()
            self.insert_channel_agent_name(channel_id)
            
        self.channel_id = channel_id

    def create_raven_channel(self):
        insert_url = f"{self.config['url']}/api/method/frappe.client.insert"
        insert_payload = {
            "doc": {
                "doctype": "Raven Channel",
                "channel_name": self.channel_name,
                "workspace": "Raven"
            }
        }

        try:
            res_insert = requests.post(insert_url, json=insert_payload, headers=self.config['headers'])
            res_insert.raise_for_status()

            response_data = res_insert.json()
            channel_id = response_data.get("message", {}).get("name")

            if not channel_id:
                frappe.throw(ErrorConfig.CREATE_CHANNEL_NO_ID.message)

            return channel_id

        except requests.exceptions.RequestException as e:
            error_msg = ErrorConfig.API_CALL_ERROR.message.format(url=self.config['url'], error=str(e))
            if e.response is not None:
                error_msg += ErrorConfig.API_CALL_DETAIL.message.format(detail=e.response.text)

            frappe.log_error(title=ErrorConfig.CREATE_CHANNEL_LOG_TITLE.message, message=error_msg)
            frappe.throw(ErrorConfig.CREATE_CHANNEL_THROW.message)

    def add_member_to_channel(self, member_email):
        add_member_url = f"{self.config['url']}/api/method/raven.api.raven_channel_member.add_channel_members"
        member_payload = {
            "channel_id": self.channel_id,
            "members": [member_email]
        }

        try:
            res_member = requests.post(add_member_url, json=member_payload, headers=self.config['headers'])
            res_member.raise_for_status()

            return True

        except requests.exceptions.RequestException as e:
            error_msg = ErrorConfig.API_CALL_ERROR.message.format(url=self.config['url'], error=str(e))
            if e.response is not None:
                error_msg += ErrorConfig.API_CALL_DETAIL.message.format(detail=e.response.text)
            frappe.log_error(title=ErrorConfig.ADD_MEMBER_LOG_TITLE.message, message=error_msg)
            frappe.throw(ErrorConfig.ADD_MEMBER_THROW.message)

    def _check_channel_is_exist(self):

            
        check_channel_is_exist_url = f"{self.config['url']}/api/method/raven.api.check_channel_is_exist.check_channel_is_exist"
        payload = {
            "channel_id": self.channel_id,
        }
        try:
            res_check = requests.post(check_channel_is_exist_url, json=payload, headers=self.config['headers'])
            return res_check.json().get("message", "")
        except requests.exceptions.RequestException as e:
            frappe.throw(str(e))

    def check_local_channel(self):
        # Lấy channel_id từ DB local dựa theo channel_name
        return frappe.db.get_value("HD Channel Agent", {"channel_agent_name": self.channel_name}, "channel_id")

    def insert_channel_agent_name(self , channel_id):
        insert_chanel_id(channel_id, self.channel_name)

    def add_user_to_chanel_site_config(self, member_email):
        """
        Hàm tổng hợp: Thêm member vào channel
        """
        # Thêm member vào channel
        self.add_member_to_channel(member_email)

        return {
            "status": "success",
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "members_added": [member_email]
        }

    def get_member_from_email(self,email):
        get_member_url = f"{self.config['url']}/api/method/raven.api.raven_channel_member.get_member_from_email"
        payload = {
            "email": email,
            "channel_id": self.channel_id,
        }
        try:
            res_check = requests.post(get_member_url, json=payload, headers=self.config['headers'])
            res_check.raise_for_status()
            
            message = res_check.json().get("message", {})
            return message.get("member_id") if isinstance(message, dict) else ""
        except requests.exceptions.RequestException as e:
            frappe.throw(str(e))

    def delete_user_in_channel(self,email):
        member_id = self.get_member_from_email(email)
        if not member_id:
            frappe.throw("Không tìm thấy member_id từ email")
    
        delete_member_url = f"{self.config['url']}/api/method/raven.api.raven_channel_member.delete_channel_member"
        payload = {
            "channel_id": self.channel_id,
            "member_id": member_id,
        }
        
        try:
            res = requests.post(delete_member_url, json=payload, headers=self.config['headers'])
            res.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            frappe.throw(str(e))

    def send_ticket_notification(self, ticket_name, subject, raised_by_email, raised_by_name):
        send_message_url = f"{self.config['url']}/api/method/raven.api.raven_message.send_message"
        
        text = f"""<div style="border:1px solid #d1d5db;border-radius:12px;padding:16px;background:#ffffff;max-width:450px;font-family:Arial,sans-serif;"><div style="font-size:18px;font-weight:bold;color:#2563eb;margin-bottom:8px;">🎫 Phiếu hỗ trợ mới</div><div style="margin-bottom:8px;"><strong>Mã phiếu:</strong> {ticket_name}</div><div style="margin-bottom:8px;"><strong>Tiêu đề:</strong> {subject}</div><div style="margin-bottom:16px;"><strong>Người xử lý phiếu:</strong> <span data-type="userMention" class="mention" data-id="{raised_by_email}" data-label="{raised_by_name}">@{raised_by_name}</span></div><a href="http://hotro.nextgrp.vn/helpdesk/tickets/{ticket_name}" target="_blank" style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;padding:10px 16px;border-radius:8px;font-weight:600;">Xem chi tiết phiếu hỗ trợ</a></div>"""

        payload = {
            "channel_id": self.channel_id,
            "text": text,
            "is_reply": 0,
            "send_silently": False,
            "workspace": "Raven"
        }

        try:
            res = requests.post(send_message_url, json=payload, headers=self.config['headers'])
            res.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            error_msg = ErrorConfig.API_CALL_ERROR.message.format(url=self.config['url'], error=str(e))
            if e.response is not None:
                error_msg += ErrorConfig.API_CALL_DETAIL.message.format(detail=e.response.text)
            frappe.log_error(title=ErrorConfig.SEND_MESSAGE_LOG_TITLE.message, message=error_msg)
            raise CommonException(ErrorConfig.SEND_MESSAGE_THROW)


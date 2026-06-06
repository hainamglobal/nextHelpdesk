import frappe
import requests
from helpdesk.config.config_sites import get_nextgrp_develop_config
from helpdesk.config.error_config import ErrorConfig
from helpdesk.repository.hd_agent_channel_repository import insert_chanel_id


class RavenChannelService:
    def __init__(self):
        self.config = get_nextgrp_develop_config()
        self.channel_name = "Nhóm hỗ trợ khách hàng nextGrp"

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
        Hàm tổng hợp: 
        1. Kiểm tra xem DB local đã lưu channel_id cho channel_name này chưa.
        2. Nếu chưa có: Tạo Raven Channel trên site develop -> Lấy ID mới -> Lưu xuống DB local.
        3. Nếu đã có: Lấy luôn ID đó.
        4. Gọi API add_channel_members.
        """
        
        # Bước 1: Kiểm tra trong DB local
        channel_id = self.check_local_channel()
        
        if not channel_id:
            # Bước 2: Chưa có thì tạo mới trên site develop
            channel_id = self.create_raven_channel()
            # Lưu xuống DB local để dùng cho các user sau
            self.insert_channel_agent_name(channel_id)
            
        # Cập nhật ID để dùng trong add_member_to_channel
        self.channel_id = channel_id

        # Thêm member vào channel
        self.add_member_to_channel(member_email)

        return {
            "status": "success",
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "members_added": [member_email]
        }

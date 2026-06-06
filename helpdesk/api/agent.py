import frappe
from helpdesk.service.add_user_to_chanel import RavenChannelService

@frappe.whitelist()
def sent_invites(emails, send_welcome_mail_to_user=True):
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
            frappe.get_doc(doc).insert()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error("Lỗi sent_invites (HD Agent)", frappe.get_traceback())
        frappe.throw(f"Đã xảy ra lỗi trong quá trình tạo Agent. Đã rollback dữ liệu. Chi tiết lỗi: {str(e)}")

    return

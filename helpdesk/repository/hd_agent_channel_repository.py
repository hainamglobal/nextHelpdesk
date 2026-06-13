import frappe

def insert_chanel_id(channel_id, channel_agent_name):
    # Kiểm tra agent đã tồn tại trong channel chưa
    existing_channel = frappe.db.get_value(
        "HD Channel Agent",
        {
            "channel_id": channel_id,
            "channel_agent_name": channel_agent_name
        },
        "channel_id"
    )

    # Nếu đã tồn tại thì trả về channel_id
    if existing_channel:
        return existing_channel

    # Nếu chưa tồn tại thì tạo mới
    doc = frappe.get_doc({
        "doctype": "HD Channel Agent",
        "channel_id": channel_id,
        "channel_agent_name": channel_agent_name
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return doc.channel_id

def get_channel_id(channel_name):
    # Lấy channel_id từ DB local dựa theo channel_name
    return frappe.db.get_value("HD Channel Agent", {"channel_agent_name": channel_name}, "channel_id")


def count_channel_id(channel_name) :
    count = frappe.db.count("HD Channel Agent", {"channel_agent_name":channel_name})
    return count
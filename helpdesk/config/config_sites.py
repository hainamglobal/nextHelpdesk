import frappe

def get_nextgrp_develop_config():
    """Lấy thông tin cấu hình từ HD Site Config"""
    
    organization = frappe.conf.get("organization")
    
    config = frappe.get_all(
        "HD Site Config",
        filters={"organization": organization},
        fields=["name", "site_url", "api_key"],
        limit=1
    )
    
    if not config:
        frappe.throw("Chưa cấu hình thông tin trong HD Site Config")
        
    config_doc = config[0]
    api_key = config_doc.get("api_key")
    base_url = config_doc.get("site_url")
    
    try:
        api_secret = frappe.utils.password.get_decrypted_password("HD Site Config", config_doc.name, "api_secret")
    except Exception:
        api_secret = None
    
    if not api_key or not api_secret:
        frappe.throw("Chưa cấu hình api_key hoặc api_secret trong HD Site Config")
        
    return {
        "url": base_url,
        "api_key": api_key,
        "api_secret": api_secret,
        "headers": {
            "Authorization": f"token {api_key}:{api_secret}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    }

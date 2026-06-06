import frappe

def get_nextgrp_develop_config():
    """Lấy thông tin cấu hình của site develop.nextgrp.vn từ site_config.json"""
    api_key = frappe.conf.get("api_key")
    api_secret = frappe.conf.get("api_secret")
    base_url = frappe.conf.get("site_url")
    
    if not api_key or not api_secret:
        frappe.throw("Chưa cấu hình api_key_develop hoặc api_secret_develop trong site_config.json")
        
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

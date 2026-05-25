import frappe
import os
import json

def execute():
    # Force delete the corrupted record if it exists
    if frappe.db.exists("DocType", "Leapsys ESS App Settings"):
        frappe.delete_doc("DocType", "Leapsys ESS App Settings", ignore_missing=True, force=True)
    
    # Get the exact absolute path to the JSON file relative to THIS patch file
    # This patch is at apps/leapsys_ess_backend/leapsys_ess_backend/patches/force_sync2.py
    patch_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(os.path.dirname(patch_dir), "doctype", "leapsys_ess_app_settings", "leapsys_ess_app_settings.json")
    
    with open(json_path, "r") as f:
        doc_dict = json.load(f)
    
    # Manually insert the DocType into the database
    doc = frappe.get_doc(doc_dict)
    doc.insert(ignore_permissions=True, ignore_if_duplicate=True)

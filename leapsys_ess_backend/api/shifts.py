import frappe
from leapsys_ess_backend.api.utils import get_current_employee

@frappe.whitelist()
def get_shift_requests():
    """Fetch employee's shift requests"""
    try:
        employee = get_current_employee()
        requests = frappe.get_all(
            "Shift Request",
            filters={"employee": employee},
            fields=["name", "shift_type", "from_date", "to_date", "status"],
            order_by="creation desc",
            limit=20
        )
        return {"success": True, "data": requests}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def submit_shift_request(shift_type, from_date, to_date, reason):
    """Submit a new shift request"""
    try:
        employee = get_current_employee()
        
        # Make sure Shift Type exists
        if not frappe.db.exists("Shift Type", shift_type):
            return {"success": False, "error": f"Shift Type {shift_type} not found"}

        sr = frappe.get_doc({
            "doctype": "Shift Request",
            "employee": employee,
            "shift_type": shift_type,
            "from_date": from_date,
            "to_date": to_date,
            "reason": reason,
            "status": "Draft"
        })
        sr.insert(ignore_permissions=True)
        return {"success": True, "message": "Shift Request submitted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

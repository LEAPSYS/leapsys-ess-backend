import frappe

@frappe.whitelist()
def get_employee_directory():
    """Fetch basic info of all active employees"""
    try:
        employees = frappe.get_all(
            "Employee",
            filters={"status": "Active"},
            fields=["name", "employee_name", "department", "designation", "cell_number", "personal_email", "company_email", "image"],
            order_by="employee_name asc"
        )
        return {"success": True, "data": employees}
    except Exception as e:
        return {"success": False, "error": str(e)}

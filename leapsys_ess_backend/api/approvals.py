import frappe
from leapsys_ess_backend.api.utils import get_current_employee

@frappe.whitelist()
def get_pending_approvals():
    """Fetch pending leaves and expenses for the logged-in manager's subordinates"""
    try:
        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user, "status": "Active"}, "name")
        
        if not employee:
            return {"success": False, "error": "User is not linked to an active Employee"}

        # Leaves
        leaves = frappe.get_all(
            "Leave Application",
            filters={"leave_approver": user, "status": "Open"},
            fields=["name", "employee", "employee_name", "leave_type", "from_date", "to_date", "total_leave_days"]
        )

        # Expenses
        expenses = frappe.get_all(
            "Expense Claim",
            filters={"expense_approver": user, "approval_status": "Draft"},
            fields=["name", "employee", "employee_name", "grand_total", "posting_date"]
        )

        return {"success": True, "data": {"leaves": leaves, "expenses": expenses}}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def submit_approval(doctype, docname, action):
    """Approve or Reject a document. Action should be 'Approve' or 'Reject'"""
    try:
        if doctype not in ["Leave Application", "Expense Claim"]:
            return {"success": False, "error": "Invalid doctype"}

        doc = frappe.get_doc(doctype, docname)
        
        # We assume standard Frappe workflow. If they don't have Workflow, just set status.
        if doctype == "Leave Application":
            doc.status = "Approved" if action == "Approve" else "Rejected"
        else: # Expense Claim
            doc.approval_status = "Approved" if action == "Approve" else "Rejected"
            if action == "Approve":
                doc.status = "Approved"
            else:
                doc.status = "Rejected"

        doc.save(ignore_permissions=True)
        if action == "Approve" and doctype == "Leave Application":
            doc.submit() # Leaves require submit
            
        return {"success": True, "message": f"{doctype} {action}d successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

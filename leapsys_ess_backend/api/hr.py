import frappe
from frappe import _
from leapsys_ess_backend.api.utils import get_current_employee

@frappe.whitelist()
def get_leave_balances():
    """Fetch leave balances for an employee"""
    try:
        employee = get_current_employee()
        balances = frappe.get_all(
            "Leave Allocation",
            filters={"employee": employee, "docstatus": 1},
            fields=["leave_type", "total_leaves_allocated", "new_leaves_allocated"]
        )
        return {"success": True, "data": balances}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def submit_expense_claim(expense_type, amount, date, description):
    """Submit a new expense claim"""
    try:
        employee = get_current_employee()
        employee_doc = frappe.get_doc("Employee", employee)
        expense = frappe.get_doc({
            "doctype": "Expense Claim",
            "employee": employee,
            "company": employee_doc.company,
            "posting_date": date or frappe.utils.today(),
            "exchange_rate": 1,
            "expenses": [{
                "expense_type": expense_type,
                "amount": amount,
                "expense_date": date or frappe.utils.today(),
                "description": description
            }]
        })
        expense.insert(ignore_permissions=True)
        return {"success": True, "message": "Expense Claim submitted successfully.", "name": expense.name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_salary_slips():
    """Fetch salary slips for the employee"""
    try:
        employee = get_current_employee()
        slips = frappe.get_all(
            "Salary Slip",
            filters={"employee": employee, "docstatus": 1},
            fields=["name", "start_date", "end_date", "gross_pay", "net_pay"],
            order_by="start_date desc"
        )
        return {"success": True, "data": slips}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_leave_types():
    try:
        types = frappe.get_all("Leave Type", fields=["name"])
        return {"success": True, "data": types}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def create_leave_application(leave_type, from_date, to_date, reason, half_day=0, half_day_date=None):
    try:
        employee = get_current_employee()
        employee_doc = frappe.get_doc("Employee", employee)
        
        doc_args = {
            "doctype": "Leave Application",
            "employee": employee,
            "company": employee_doc.company,
            "leave_type": leave_type,
            "from_date": from_date,
            "to_date": to_date,
            "description": reason,
            "status": "Open",
            "half_day": int(half_day)
        }
        
        if int(half_day) == 1:
            doc_args["half_day_date"] = half_day_date or from_date
            
        leave = frappe.get_doc(doc_args)
        leave.insert(ignore_permissions=True)
        return {"success": True, "message": "Leave Application submitted successfully", "name": leave.name}
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_my_expenses():
    try:
        employee = get_current_employee()
        expenses = frappe.get_all(
            "Expense Claim",
            filters={"employee": employee},
            fields=["name", "posting_date", "total_claimed_amount", "total_sanctioned_amount", "status"],
            order_by="posting_date desc"
        )
        return {"success": True, "data": expenses}
    except Exception as e:
        return {"success": False, "error": str(e)}

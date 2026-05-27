import frappe
from frappe import _
from frappe.utils import today

@frappe.whitelist()
def get_dashboard_summary():
    if frappe.session.user == 'Guest':
        frappe.throw(_("Not logged in"), frappe.AuthenticationError)
        
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    
    summary = {}
    
    if employee:
        # Attendance (today)
        att = frappe.db.get_value("Attendance", {"employee": employee, "attendance_date": today(), "docstatus": 1}, "in_time")
        summary["attendance"] = att.strftime("%I:%M %p") if att else "No punch-in"
        
        # Leaves (balance)
        # simplistic approach, real approach is more complex
        alloc = frappe.db.sql("""
            select sum(total_leaves_allocated) as total
            from `tabLeave Allocation`
            where employee = %s and from_date <= %s and to_date >= %s and docstatus = 1
        """, (employee, today(), today()), as_dict=True)
        allocated = alloc[0].total if alloc and alloc[0].total else 0
        
        taken_sql = frappe.db.sql("""
            select sum(total_leave_days) as taken
            from `tabLeave Application`
            where employee = %s and from_date <= %s and docstatus = 1
        """, (employee, today()), as_dict=True)
        taken = taken_sql[0].taken if taken_sql and taken_sql[0].taken else 0
        
        summary["leaves"] = f"{max(0, allocated - taken)} Bal"
        
        # Expenses (unpaid/unapproved)
        # Using Expense Claim
        exp = frappe.db.get_value("Expense Claim", {"employee": employee, "docstatus": 0}, "sum(total_claimed_amount)") or 0
        summary["expenses"] = f"₹{exp}"
        
        # Salary Slips (latest)
        slip = frappe.get_all("Salary Slip", filters={"employee": employee, "docstatus": 1}, order_by="start_date desc", limit=1, fields=["month"])
        summary["salary_slips"] = slip[0].month if slip else "None"
        
        # Visits (today)
        visits = frappe.db.count("Maintenance Visit", {"maintenance_date": today(), "docstatus": ("<", 2)})
        summary["visits"] = f"{visits} Today"
        
        # Approvals (pending)
        approvals = frappe.db.count("Workflow Action", {"status": "Open", "user": frappe.session.user})
        summary["approvals"] = f"{approvals} Pending"
        
        # Shifts
        shifts = frappe.db.count("Shift Request", {"employee": employee, "docstatus": 0})
        summary["shifts"] = f"{shifts} Request"
    else:
        summary.update({
            "attendance": "--", "leaves": "--", "expenses": "--", "salary_slips": "--", "visits": "--", "approvals": "--", "shifts": "--"
        })
        
    # Projects
    projects = frappe.db.count("Project", {"status": "Open"})
    summary["projects"] = f"{projects} Active"
    
    # Directory
    employees = frappe.db.count("Employee", {"status": "Active"})
    summary["directory"] = f"{employees} Emp"
    
    # Todos
    todos = frappe.db.count("ToDo", {"owner": frappe.session.user, "status": "Open"})
    summary["todos"] = f"{todos} Pending"
    
    frappe.local.response["message"] = {
        "success": True,
        "summary": summary
    }

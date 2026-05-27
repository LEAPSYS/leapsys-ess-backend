import frappe
from frappe import _
from frappe.utils import today

@frappe.whitelist()
def get_dashboard_summary():
    """Return dashboard summary data. Each section is wrapped in try/except
    so a single query failure does not break the entire dashboard."""
    if frappe.session.user == 'Guest':
        frappe.throw(_("Not logged in"), frappe.AuthenticationError)
        
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    
    summary = {
        "attendance": "--",
        "leaves": "--",
        "expenses": "--",
        "salary_slips": "--",
        "visits": "--",
        "approvals": "--",
        "shifts": "--",
        "projects": "--",
        "directory": "--",
        "todos": "--"
    }
    
    if employee:
        # Attendance (today)
        try:
            att = frappe.db.get_value("Attendance",
                {"employee": employee, "attendance_date": today(), "docstatus": 1}, "in_time")
            summary["attendance"] = att.strftime("%I:%M %p") if att else "No check-in"
        except Exception:
            summary["attendance"] = "No check-in"
        
        # Leaves (balance)
        try:
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
        except Exception:
            summary["leaves"] = "0 Bal"
        
        # Expenses (draft / unapproved)
        try:
            exp = frappe.db.sql(
                "select sum(total_claimed_amount) as total from `tabExpense Claim` where employee=%s and docstatus=0",
                employee, as_dict=True)
            exp_total = exp[0].total if exp and exp[0].total else 0
            summary["expenses"] = f"₹{exp_total}"
        except Exception:
            summary["expenses"] = "₹0"
        
        # Salary Slips (latest)
        try:
            slip = frappe.get_all("Salary Slip",
                filters={"employee": employee, "docstatus": 1},
                order_by="start_date desc", limit=1, fields=["start_date"])
            summary["salary_slips"] = slip[0].start_date.strftime("%b %Y") if slip and slip[0].start_date else "None"
        except Exception:
            summary["salary_slips"] = "None"
        
        # Visits (today)
        try:
            visits = frappe.db.count("Maintenance Visit", {"mntc_date": today(), "docstatus": ("<", 2)})
            summary["visits"] = f"{visits} Today"
        except Exception:
            summary["visits"] = "0 Today"
        
        # Approvals (pending)
        try:
            approvals = frappe.db.count("Workflow Action", {"status": "Open", "user": frappe.session.user})
            summary["approvals"] = f"{approvals} Pending"
        except Exception:
            summary["approvals"] = "0 Pending"
        
        # Shifts
        try:
            shifts = frappe.db.count("Shift Request", {"employee": employee, "docstatus": 0})
            summary["shifts"] = f"{shifts} Request"
        except Exception:
            summary["shifts"] = "0 Request"
    
    # Projects
    try:
        projects = frappe.db.count("Project", {"status": "Open"})
        summary["projects"] = f"{projects} Active"
    except Exception:
        summary["projects"] = "0 Active"
    
    # Directory
    try:
        employees = frappe.db.count("Employee", {"status": "Active"})
        summary["directory"] = f"{employees} Emp"
    except Exception:
        summary["directory"] = "0 Emp"
    
    # Todos
    try:
        todos = frappe.db.count("ToDo", {"allocated_to": frappe.session.user, "status": "Open"})
        summary["todos"] = f"{todos} Pending"
    except Exception:
        summary["todos"] = "0 Pending"
    
    frappe.local.response["message"] = {
        "success": True,
        "summary": summary
    }

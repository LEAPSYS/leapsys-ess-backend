import frappe

@frappe.whitelist()
def get_todos():
    """Fetch user's open ToDos"""
    try:
        user = frappe.session.user
        todos = frappe.get_all(
            "ToDo",
            filters={"allocated_to": user, "status": "Open"},
            fields=["name", "description", "priority", "date"],
            order_by="date asc, creation desc"
        )
        return {"success": True, "data": todos}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def create_todo(description, date=None, priority="Medium"):
    """Create a new ToDo"""
    try:
        user = frappe.session.user
        todo = frappe.get_doc({
            "doctype": "ToDo",
            "description": description,
            "allocated_to": user,
            "date": date,
            "priority": priority,
            "status": "Open"
        })
        todo.insert(ignore_permissions=True)
        return {"success": True, "message": "ToDo created"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def complete_todo(todo_name):
    """Mark a ToDo as Closed"""
    try:
        todo = frappe.get_doc("ToDo", todo_name)
        # Ensure they own it
        if todo.allocated_to != frappe.session.user:
            return {"success": False, "error": "Not authorized"}
            
        todo.status = "Closed"
        todo.save(ignore_permissions=True)
        return {"success": True, "message": "ToDo completed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

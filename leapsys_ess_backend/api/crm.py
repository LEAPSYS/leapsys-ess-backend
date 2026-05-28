import frappe
import json

@frappe.whitelist()
def get_customers():
    try:
        customers = frappe.get_all("Customer", fields=["name", "customer_name", "customer_group"])
        return {"success": True, "data": customers}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_leads():
    try:
        leads = frappe.get_all("Lead", fields=["name", "lead_name", "status", "company_name", "email_id", "mobile_no"], order_by="creation desc")
        return {"success": True, "data": leads}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_lead_details(name):
    try:
        lead = frappe.get_doc("Lead", name)
        return {"success": True, "data": lead.as_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def create_lead(lead_name, company_name=None, email_id=None, mobile_no=None, status="Lead"):
    try:
        doc = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": lead_name,
            "company_name": company_name,
            "email_id": email_id,
            "mobile_no": mobile_no,
            "status": status
        })
        doc.insert(ignore_permissions=True)
        return {"success": True, "data": doc.name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def update_lead(name, data):
    try:
        updates = json.loads(data)
        doc = frappe.get_doc("Lead", name)
        doc.update(updates)
        doc.save(ignore_permissions=True)
        return {"success": True, "data": doc.name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_opportunities():
    try:
        opps = frappe.get_all("Opportunity", fields=["name", "opportunity_from", "party_name", "opportunity_amount", "status", "expected_closing"], order_by="creation desc")
        return {"success": True, "data": opps}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_opportunity_details(name):
    try:
        opp = frappe.get_doc("Opportunity", name)
        return {"success": True, "data": opp.as_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def create_opportunity(party_type, party_name, expected_closing=None, opportunity_amount=0):
    try:
        doc = frappe.get_doc({
            "doctype": "Opportunity",
            "opportunity_from": party_type,
            "party_name": party_name,
            "expected_closing": expected_closing,
            "opportunity_amount": opportunity_amount,
            "status": "Open"
        })
        doc.insert(ignore_permissions=True)
        return {"success": True, "data": doc.name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def update_opportunity(name, data):
    try:
        updates = json.loads(data)
        doc = frappe.get_doc("Opportunity", name)
        doc.update(updates)
        doc.save(ignore_permissions=True)
        return {"success": True, "data": doc.name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_events():
    try:
        # Get events for the current user
        events = frappe.get_all("Event", filters={"owner": frappe.session.user}, fields=["name", "subject", "event_type", "starts_on", "ends_on", "status"], order_by="starts_on asc")
        return {"success": True, "data": events}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def create_event(subject, starts_on, ends_on, event_type="Private", location=None, description=None):
    try:
        doc = frappe.get_doc({
            "doctype": "Event",
            "subject": subject,
            "starts_on": starts_on,
            "ends_on": ends_on,
            "event_type": event_type,
            "description": description,
            "custom_location_type": location # Assuming we might want to store 'Onsite' / 'Offsite' in description or custom field. Let's just use description if custom field doesn't exist.
        })
        if location:
            doc.description = f"Location Type: {location}\n\n{description or ''}"
            
        doc.insert(ignore_permissions=True)
        return {"success": True, "data": doc.name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_items():
    try:
        items = frappe.get_all("Item", filters={"has_serial_no": 1}, fields=["name", "item_name", "item_code"])
        return {"success": True, "data": items}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_serial_nos(customer=None):
    try:
        filters = {}
        # If no customer is passed, we can't easily filter standard Serial No. In standard ERPNext, Serial No has no Customer field natively unless via Delivery Note. We'll fetch all active serial nos if customer is not reliable, or assume a custom_customer field. 
        # For safety, let's just fetch all active serial numbers.
        serial_nos = frappe.get_all("Serial No", fields=["name", "item_code", "item_name", "status"])
        return {"success": True, "data": serial_nos}
    except Exception as e:
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def register_serial_no(item_code, serial_no, lat=None, lon=None, photo_data=None):
    try:
        # Create Serial No
        doc = frappe.get_doc({
            "doctype": "Serial No",
            "item_code": item_code,
            "serial_no": serial_no,
            "status": "Active"
        })
        
        # Append geolocation to description/details to ensure it's saved without needing custom fields
        geo_info = f"Registered via Mobile App.\nGeolocation: Lat {lat}, Lon {lon}"
        doc.serial_no_details = geo_info
        
        doc.insert(ignore_permissions=True)
        
        # Handle Photo Attachment
        if photo_data:
            import base64
            # photo_data is expected to be a base64 string like "data:image/jpeg;base64,/9j/4AAQSk..."
            if "," in photo_data:
                photo_data = photo_data.split(",")[1]
            
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": f"{serial_no}_registration.jpg",
                "attached_to_doctype": "Serial No",
                "attached_to_name": doc.name,
                "content": photo_data,
                "decode": True,
                "is_private": 0
            })
            file_doc.insert(ignore_permissions=True)
        
        return {"success": True, "data": doc.name}
    except Exception as e:
        return {"success": False, "error": str(e)}

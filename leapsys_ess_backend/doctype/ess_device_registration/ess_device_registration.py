from frappe.model.document import Document

class ESSDeviceRegistration(Document):
    def before_save(self):
        # Additional logic can be added to validate device limits per user
        pass

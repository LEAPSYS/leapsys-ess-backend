from frappe.model.document import Document

class ESSEmployeeLocationLog(Document):
    def validate(self):
        # Example: Ensure coordinates are valid floats
        if self.latitude and not isinstance(self.latitude, float):
            self.latitude = float(self.latitude)
        if self.longitude and not isinstance(self.longitude, float):
            self.longitude = float(self.longitude)

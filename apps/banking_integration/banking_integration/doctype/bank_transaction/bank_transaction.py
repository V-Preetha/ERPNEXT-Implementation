import frappe
from frappe.model.document import Document

class BankTransaction(Document):
    def on_update(self):
        self.update_audit_log()

    def update_audit_log(self):
        log_entry = f"{frappe.utils.now()}: Status changed to {self.status} by {frappe.session.user}"
        if self.audit_log:
            self.audit_log += "\n" + log_entry
        else:
            self.audit_log = log_entry
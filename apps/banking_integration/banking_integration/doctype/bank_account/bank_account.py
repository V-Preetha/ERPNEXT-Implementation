import frappe
from frappe.model.document import Document
from banking_integration.utils.encryption import encrypt_password, decrypt_password

class BankAccount(Document):
    def validate(self):
        if self.ebics_password and not self.ebics_password.startswith("***"):
            self.ebics_password = encrypt_password(self.ebics_password)

    def get_decrypted_password(self):
        return decrypt_password(self.ebics_password)
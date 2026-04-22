import frappe
from frappe.model.document import Document
from banking_integration.utils.encryption import encrypt_password, decrypt_password

class BankAccount(Document):
    def validate(self):
        if self.ebics_password and not self.ebics_password.startswith("***"):
            self.ebics_password = encrypt_password(self.ebics_password)

    def on_update(self):
        # If account status changed to Active, re-run matching for previously inactive transactions
        if self.has_value_changed('status') and self.status == 'Active':
            self.re_run_matching_for_inactive_transactions()

    def re_run_matching_for_inactive_transactions(self):
        """Re-run matching engine for transactions that were previously marked as Inactive Account."""
        try:
            # Get transactions for this IBAN that are marked as Inactive Account
            inactive_transactions = frappe.get_all('Bank Transaction',
                filters={
                    'iban': self.iban,
                    'status': 'Inactive Account'
                },
                fields=['name'])

            if inactive_transactions:
                # Import here to avoid circular imports
                from banking_integration.api.transaction import run_matching_engine
                
                # Run the matching engine which will now process these transactions
                run_matching_engine()
                
        except Exception as e:
            frappe.log_error(f"Error re-running matching for bank account {self.name}: {str(e)}", "Bank Account Status Change")

    def get_decrypted_password(self):
        return decrypt_password(self.ebics_password)
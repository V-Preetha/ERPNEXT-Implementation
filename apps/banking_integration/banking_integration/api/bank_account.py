import frappe
from frappe import _
from banking_integration.services.ebics_service import EBICSService
from banking_integration.utils.validation import validate_iban, validate_ebics_credentials

@frappe.whitelist()
def connect_bank_account(bank_account_name):
    """Test connection to bank account."""
    try:
        bank_account = frappe.get_doc('Bank Account', bank_account_name)
        if not validate_ebics_credentials(bank_account.ebics_user_id, bank_account.ebics_host_id, bank_account.ebics_partner_id):
            frappe.throw(_("Invalid EBICS credentials"))

        ebics = EBICSService(bank_account)
        if ebics.connect():
            bank_account.status = 'Active'
            bank_account.save()
            return {'status': 'success', 'message': 'Connection successful'}
        else:
            bank_account.status = 'Error'
            bank_account.save()
            return {'status': 'error', 'message': 'Connection failed'}
    except Exception as e:
        frappe.log_error(str(e), "Bank Connection Error")
        return {'status': 'error', 'message': str(e)}

@frappe.whitelist()
def sync_transactions(bank_account_name):
    """Manually sync transactions for a bank account."""
    from banking_integration.services.sync import sync_account_transactions
    try:
        sync_account_transactions(bank_account_name)
        return {'status': 'success', 'message': 'Sync completed'}
    except Exception as e:
        frappe.log_error(str(e), "Manual Sync Error")
        return {'status': 'error', 'message': str(e)}
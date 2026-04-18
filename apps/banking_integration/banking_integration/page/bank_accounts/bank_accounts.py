import frappe
from frappe import _

def get_context(context):
    context.title = _("Bank Accounts")
    context.accounts = frappe.get_all('Bank Account',
        fields=['name', 'bank_name', 'iban', 'status', 'last_sync_date'])
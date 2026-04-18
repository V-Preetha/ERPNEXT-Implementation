import frappe
from frappe import _

def get_context(context):
    context.title = _("Bank Transactions")
    context.transactions = frappe.get_all('Bank Transaction',
        fields=['name', 'transaction_date', 'amount', 'status', 'matched_payment', 'confidence_score'])
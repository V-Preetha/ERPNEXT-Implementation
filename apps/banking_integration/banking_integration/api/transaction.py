import frappe
from frappe import _
from banking_integration.services.matching_engine import MatchingEngine

@frappe.whitelist()
def run_matching_engine():
    """Run matching engine for all unmatched transactions."""
    from banking_integration.services.matching import run_matching_engine
    try:
        run_matching_engine()
        return {'status': 'success', 'message': 'Matching completed'}
    except Exception as e:
        frappe.log_error(str(e), "Matching Error")
        return {'status': 'error', 'message': str(e)}

@frappe.whitelist()
def manual_match_transaction(transaction_name, payment_name):
    """Manually match a transaction to a payment."""
    try:
        tx = frappe.get_doc('Bank Transaction', transaction_name)
        tx.matched_payment = payment_name
        tx.status = 'Manual Match'
        tx.confidence_score = 100
        tx.save()
        return {'status': 'success', 'message': 'Transaction matched'}
    except Exception as e:
        frappe.log_error(str(e), "Manual Match Error")
        return {'status': 'error', 'message': str(e)}
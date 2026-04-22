import frappe
from frappe import _
from banking_integration.services.payments import (
    get_all_payments,
    get_payment_by_id,
    get_payments_by_bank_account,
    get_payments_created_today,
    get_payment_count
)

@frappe.whitelist()
def get_payments():
    """Get all payments."""
    try:
        payments = get_all_payments()
        return {'status': 'success', 'payments': payments}
    except Exception as e:
        frappe.log_error(str(e), "Get Payments Error")
        return {'status': 'error', 'message': str(e)}

@frappe.whitelist()
def get_payment_details(payment_id):
    """Get detailed information for a specific payment."""
    try:
        payment = get_payment_by_id(payment_id)
        if not payment:
            return {'status': 'error', 'message': f'Payment {payment_id} not found'}

        return {
            'status': 'success',
            'payment': payment.to_dict()
        }
    except Exception as e:
        frappe.log_error(str(e), "Get Payment Details Error")
        return {'status': 'error', 'message': str(e)}

@frappe.whitelist()
def get_payments_by_account(bank_account):
    """Get payments filtered by bank account."""
    try:
        payments = get_payments_by_bank_account(bank_account)
        return {'status': 'success', 'payments': payments}
    except Exception as e:
        frappe.log_error(str(e), "Get Payments by Account Error")
        return {'status': 'error', 'message': str(e)}

@frappe.whitelist()
def get_payment_stats():
    """Get payment statistics for dashboard."""
    try:
        total_payments = get_payment_count()
        today_payments = len(get_payments_created_today())

        return {
            'status': 'success',
            'stats': {
                'total_payments': total_payments,
                'today_payments': today_payments
            }
        }
    except Exception as e:
        frappe.log_error(str(e), "Get Payment Stats Error")
        return {'status': 'error', 'message': str(e)}

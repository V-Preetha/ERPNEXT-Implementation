import frappe
from frappe import _
from datetime import datetime
import json

# In-memory payments database
payments_db = []

class Payment:
    """Simulated Payment model for demo purposes."""

    def __init__(self, payment_id, amount, reference, iban, bank_account, status="Completed", transaction_id=None):
        self.payment_id = payment_id
        self.amount = amount
        self.reference = reference
        self.iban = iban
        self.bank_account = bank_account
        self.status = status
        self.created_at = datetime.now()
        self.transaction_id = transaction_id

    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'amount': self.amount,
            'reference': self.reference,
            'iban': self.iban,
            'bank_account': self.bank_account,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'transaction_id': self.transaction_id
        }

def get_next_payment_id():
    """Generate next payment ID (PAY-001, PAY-002, etc.)"""
    if not payments_db:
        return "PAY-001"

    # Find the highest PAY-XXX number
    max_num = 0
    for payment in payments_db:
        if payment.payment_id.startswith('PAY-'):
            try:
                num = int(payment.payment_id.split('-')[1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                continue

    return f"PAY-{str(max_num + 1).zfill(3)}"

def create_payment(amount, reference, iban, bank_account, transaction_id=None):
    """Create a new payment and store it in the database."""
    payment_id = get_next_payment_id()
    payment = Payment(
        payment_id=payment_id,
        amount=amount,
        reference=reference,
        iban=iban,
        bank_account=bank_account,
        transaction_id=transaction_id
    )
    payments_db.append(payment)
    return payment

def get_payment_by_id(payment_id):
    """Get payment by ID."""
    for payment in payments_db:
        if payment.payment_id == payment_id:
            return payment
    return None

def get_all_payments():
    """Get all payments."""
    return [payment.to_dict() for payment in payments_db]

def get_payments_by_bank_account(bank_account):
    """Get payments filtered by bank account."""
    return [payment.to_dict() for payment in payments_db if payment.bank_account == bank_account]

def get_payments_created_today():
    """Get payments created today."""
    today = datetime.now().date()
    return [payment.to_dict() for payment in payments_db if payment.created_at.date() == today]

def get_payment_count():
    """Get total number of payments."""
    return len(payments_db)

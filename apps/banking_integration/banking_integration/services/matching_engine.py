import frappe
from difflib import SequenceMatcher
import re

class MatchingEngine:
    """Engine for matching bank transactions to payments/invoices."""

    def __init__(self):
        self.weights = {
            'amount': 0.4,
            'iban': 0.3,
            'reference': 0.2,
            'name': 0.1
        }

    def calculate_confidence(self, transaction, payment):
        """Calculate confidence score for a match."""
        score = 0

        # Amount match (exact)
        if abs(transaction.amount - payment.paid_amount) < 0.01:
            score += self.weights['amount']
        elif abs(transaction.amount - payment.paid_amount) < 1:
            score += self.weights['amount'] * 0.5

        # IBAN match
        if transaction.iban and payment.party_bank_account:
            if transaction.iban == payment.party_bank_account:
                score += self.weights['iban']

        # Reference match
        if transaction.reference and payment.reference_no:
            similarity = SequenceMatcher(None, transaction.reference.lower(), payment.reference_no.lower()).ratio()
            score += self.weights['reference'] * similarity

        # Name match
        if transaction.name and payment.party_name:
            similarity = SequenceMatcher(None, transaction.name.lower(), payment.party_name.lower()).ratio()
            score += self.weights['name'] * similarity

        return int(score * 100)

    def find_matches(self, transaction):
        """Find potential matches for a transaction."""
        # Get open payments/invoices
        payments = frappe.get_all('Payment Entry',
            filters={'docstatus': 1, 'payment_type': 'Receive', 'unallocated_amount': ['>', 0]},
            fields=['name', 'paid_amount', 'party_name', 'reference_no', 'party_bank_account'])

        matches = []
        for payment in payments:
            confidence = self.calculate_confidence(transaction, payment)
            if confidence > 0:
                matches.append({
                    'payment': payment.name,
                    'confidence': confidence,
                    'reason': f"Amount: {transaction.amount}, IBAN: {transaction.iban}, Ref: {transaction.reference}"
                })

        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches[:10]  # Top 10

    def auto_match(self, transaction):
        """Auto match if confidence >= 90."""
        matches = self.find_matches(transaction)
        if matches and matches[0]['confidence'] >= 90:
            return matches[0]
        return None

    def detect_chargeback(self, transaction):
        """Detect if transaction is a chargeback."""
        # Simple detection: negative amount with reference to previous transaction
        if transaction.amount < 0 and transaction.reference:
            # Check if there's a positive transaction with similar reference
            positive_tx = frappe.get_all('Bank Transaction',
                filters={'reference': transaction.reference, 'amount': -transaction.amount},
                fields=['name'])
            if positive_tx:
                return True
        return False
import frappe
from difflib import SequenceMatcher
import re
import json
from banking_integration.utils.validation import validate_iban, get_bank_account_by_iban, is_account_active
from banking_integration.services.payments import create_payment, get_payment_by_id

class MatchingEngine:
    """Engine for matching bank transactions to payments/invoices with explainability."""

    def __init__(self):
        self.weights = {
            'amount': 0.4,
            'iban': 0.3,
            'reference': 0.2,
            'name': 0.1
        }

    def calculate_confidence(self, transaction, payment):
        """Calculate confidence score for a match with detailed explanation.
        
        Returns: {
            'score': 0-100,
            'matched': bool,
            'explanation': {
                'amount_match': {'score': 0-100, 'matched': bool, 'reason': str},
                'iban_match': {'score': 0-100, 'matched': bool, 'reason': str},
                'reference_match': {'score': 0-100, 'matched': bool, 'reason': str},
                'name_match': {'score': 0-100, 'matched': bool, 'reason': str}
            },
            'warnings': []
        }
        """
        explanation = {
            'amount_match': {'score': 0, 'matched': False, 'reason': ''},
            'iban_match': {'score': 0, 'matched': False, 'reason': ''},
            'reference_match': {'score': 0, 'matched': False, 'reason': ''},
            'name_match': {'score': 0, 'matched': False, 'reason': ''}
        }
        warnings = []
        score = 0

        # Amount match (exact or within tolerance)
        try:
            trans_amt = float(transaction.get('amount', 0))
            payment_amt = float(payment.get('paid_amount', 0))
            if abs(trans_amt - payment_amt) < 0.01:
                score_component = 100
                explanation['amount_match'] = {
                    'score': 100,
                    'matched': True,
                    'reason': f'Exact amount match: €{trans_amt:.2f}'
                }
            elif abs(trans_amt - payment_amt) < 1.00:
                score_component = 50
                explanation['amount_match'] = {
                    'score': 50,
                    'matched': True,
                    'reason': f'Amount within tolerance: €{trans_amt:.2f} vs €{payment_amt:.2f}'
                }
            else:
                explanation['amount_match'] = {
                    'score': 0,
                    'matched': False,
                    'reason': f'Amount mismatch: €{trans_amt:.2f} vs €{payment_amt:.2f}'
                }
                score_component = 0
            score += self.weights['amount'] * (score_component / 100)
        except Exception as e:
            warnings.append(f'Amount comparison error: {str(e)}')

        # IBAN match
        trans_iban = transaction.get('iban', '').upper().strip()
        payment_iban = payment.get('party_bank_account', '').upper().strip()
        
        if trans_iban and payment_iban:
            if trans_iban == payment_iban:
                explanation['iban_match'] = {
                    'score': 100,
                    'matched': True,
                    'reason': f'IBAN exact match: {trans_iban}'
                }
                score += self.weights['iban']
            else:
                explanation['iban_match'] = {
                    'score': 0,
                    'matched': False,
                    'reason': f'IBAN mismatch: {trans_iban} vs {payment_iban}'
                }
        elif not trans_iban:
            warnings.append('Transaction IBAN missing')
        elif not payment_iban:
            warnings.append('Payment bank account missing')

        # Reference match (fuzzy)
        trans_ref = transaction.get('reference', '').lower().strip()
        payment_ref = payment.get('reference_no', '').lower().strip()
        
        if trans_ref and payment_ref:
            similarity = SequenceMatcher(None, trans_ref, payment_ref).ratio()
            score_component = int(similarity * 100)
            if similarity >= 0.8:
                explanation['reference_match'] = {
                    'score': score_component,
                    'matched': True,
                    'reason': f'Reference match: "{trans_ref}" vs "{payment_ref}" ({int(similarity*100)}%)'
                }
            elif similarity >= 0.5:
                explanation['reference_match'] = {
                    'score': score_component,
                    'matched': 'Partial',
                    'reason': f'Partial reference match ({int(similarity*100)}%): "{trans_ref}" vs "{payment_ref}"'
                }
            else:
                explanation['reference_match'] = {
                    'score': 0,
                    'matched': False,
                    'reason': f'Reference mismatch: "{trans_ref}" vs "{payment_ref}"'
                }
            score += self.weights['reference'] * (score_component / 100)
        elif not trans_ref:
            warnings.append('Transaction reference missing')
        elif not payment_ref:
            warnings.append('Payment reference missing')

        # Name match (fuzzy)
        trans_name = transaction.get('name', '').lower().strip()
        payment_name = payment.get('party_name', '').lower().strip()
        
        if trans_name and payment_name:
            similarity = SequenceMatcher(None, trans_name, payment_name).ratio()
            score_component = int(similarity * 100)
            if similarity >= 0.8:
                explanation['name_match'] = {
                    'score': score_component,
                    'matched': True,
                    'reason': f'Name match: "{trans_name}" vs "{payment_name}" ({int(similarity*100)}%)'
                }
            elif similarity >= 0.5:
                explanation['name_match'] = {
                    'score': score_component,
                    'matched': 'Partial',
                    'reason': f'Partial name match ({int(similarity*100)}%): "{trans_name}" vs "{payment_name}"'
                }
            else:
                explanation['name_match'] = {
                    'score': 0,
                    'matched': False,
                    'reason': f'Name mismatch: "{trans_name}" vs "{payment_name}"'
                }
            score += self.weights['name'] * (score_component / 100)

        final_score = int(score * 100)
        return {
            'score': final_score,
            'matched': final_score >= 90,
            'explanation': explanation,
            'warnings': warnings
        }

    def find_matches(self, transaction):
        """Find potential matches for a transaction with explanations."""
        # Validate IBAN first
        trans_iban = transaction.get('iban', '').upper().strip()
        account_info = get_bank_account_by_iban(trans_iban) if trans_iban else None
        
        if not account_info:
            return {
                'status': 'invalid_iban',
                'message': f'IBAN {trans_iban} not found in Bank Accounts',
                'matches': []
            }
        
        if account_info.get('status') != 'Active':
            return {
                'status': 'inactive_account',
                'message': f'Bank account {account_info.get("bank_name")} is not active',
                'matches': []
            }

        # Create simulated payments for matching
        # In a real system, these would be existing payments/invoices
        simulated_payments = self._create_simulated_payments_for_matching(account_info)
        
        matches = []
        for payment in simulated_payments:
            result = self.calculate_confidence(transaction, payment)
            if result['score'] > 0:
                matches.append({
                    'payment': payment.get('payment_id'),
                    'score': result['score'],
                    'matched': result['matched'],
                    'explanation': result['explanation'],
                    'warnings': result['warnings']
                })

        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'status': 'success',
            'message': f'Found {len(matches[:10])} potential matches',
            'account_info': account_info,
            'matches': matches[:10]
        }

    def auto_match(self, transaction):
        """Auto match if confidence >= 90, with validation."""
        result = self.find_matches(transaction)
        
        if result['status'] != 'success':
            return {
                'matched': False,
                'status': result['status'],
                'message': result['message']
            }
        
        if result['matches'] and result['matches'][0]['matched']:
            return {
                'matched': True,
                'payment': result['matches'][0]['payment'],
                'score': result['matches'][0]['score'],
                'explanation': result['matches'][0]['explanation']
            }
        
        return {
            'matched': False,
            'status': 'no_match',
            'message': 'No matches with confidence >= 90',
            'top_candidate': result['matches'][0] if result['matches'] else None
        }

    def _create_simulated_payments_for_matching(self, account_info):
        """Create simulated payments for matching based on account info."""
        # This simulates payments that would exist in a real ERP system
        # In a real implementation, these would be fetched from the database
        bank_account = account_info.get('name', 'Unknown')
        
        # Create some sample payments for matching
        simulated_payments = [
            {
                'payment_id': 'PAY-001',
                'paid_amount': 1500.00,
                'party_name': 'Customer A',
                'reference_no': 'INV-2024-001',
                'party_bank_account': account_info.get('iban')
            },
            {
                'payment_id': 'PAY-002', 
                'paid_amount': 2500.00,
                'party_name': 'Customer B',
                'reference_no': 'INV-2024-002',
                'party_bank_account': account_info.get('iban')
            },
            {
                'payment_id': 'PAY-003',
                'paid_amount': 750.00,
                'party_name': 'Customer C', 
                'reference_no': 'INV-2024-003',
                'party_bank_account': account_info.get('iban')
            },
            {
                'payment_id': 'PAY-004',
                'paid_amount': 3200.00,
                'party_name': 'Customer D',
                'reference_no': 'INV-2024-004',
                'party_bank_account': account_info.get('iban')
            }
        ]
        
        return simulated_payments

        return False
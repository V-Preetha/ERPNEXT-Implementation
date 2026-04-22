import frappe
import json
from frappe import _
from banking_integration.services.matching_engine import MatchingEngine
from banking_integration.utils.validation import validate_iban, is_account_active, get_bank_account_by_iban
from banking_integration.services.payments import create_payment

@frappe.whitelist()
def run_matching_engine():
    """Run matching engine for all unmatched transactions with explanations."""
    try:
        # Include transactions that might need re-validation (Unmatched, Invalid IBAN, Inactive Account)
        processable_txs = frappe.get_all('Bank Transaction',
            filters={'status': ['in', ['Unmatched', 'Invalid IBAN', 'Inactive Account']]},
            fields=['name', 'amount', 'iban', 'reference', 'name as counterparty'],
            limit_page_length=None)
        
        engine = MatchingEngine()
        results = {
            'total': len(processable_txs),
            'matched': 0,
            'invalid_iban': 0,
            'inactive_account': 0,
            'no_match': 0,
            'matches': []
        }
        
        for tx in processable_txs:
            tx_dict = tx
            match_result = engine.auto_match(tx_dict)
            
            if match_result['matched']:
                # Create a real payment record
                tx_doc = frappe.get_doc('Bank Transaction', tx.name)
                account_info = get_bank_account_by_iban(tx.get('iban'))
                
                # Create payment with transaction details
                payment = create_payment(
                    amount=tx.get('amount'),
                    reference=tx.get('reference', f'Transaction {tx.name}'),
                    iban=tx.get('iban'),
                    bank_account=account_info.get('name') if account_info else 'Unknown',
                    transaction_id=tx.name
                )
                
                tx_doc.matched_payment = payment.payment_id
                tx_doc.status = 'Matched'
                tx_doc.confidence_score = match_result['score']
                tx_doc.match_explanation = json.dumps(match_result['explanation'])
                tx_doc.save()
                results['matched'] += 1
                results['matches'].append({
                    'transaction': tx.name,
                    'payment': payment.payment_id,
                    'score': match_result['score']
                })
            elif match_result['status'] == 'invalid_iban':
                tx_doc = frappe.get_doc('Bank Transaction', tx.name)
                tx_doc.status = 'Invalid IBAN'
                tx_doc.confidence_score = 0
                tx_doc.matched_payment = None
                tx_doc.match_explanation = None
                tx_doc.save()
                results['invalid_iban'] += 1
            elif match_result['status'] == 'inactive_account':
                tx_doc = frappe.get_doc('Bank Transaction', tx.name)
                tx_doc.status = 'Inactive Account'
                tx_doc.confidence_score = 0
                tx_doc.matched_payment = None
                tx_doc.match_explanation = None
                tx_doc.save()
                results['inactive_account'] += 1
            else:
                # Reset status to Unmatched if it was previously invalid but now valid
                tx_doc = frappe.get_doc('Bank Transaction', tx.name)
                if tx_doc.status in ['Invalid IBAN', 'Inactive Account']:
                    tx_doc.status = 'Unmatched'
                    tx_doc.confidence_score = 0
                    tx_doc.matched_payment = None
                    tx_doc.match_explanation = None
                    tx_doc.save()
                results['no_match'] += 1
        
        return {'status': 'success', 'message': 'Matching completed', 'results': results}
    except Exception as e:
        frappe.log_error(str(e), "Matching Engine Error")
        return {'status': 'error', 'message': str(e)}

@frappe.whitelist()
def get_match_suggestions(transaction_name):
    """Get detailed match suggestions with explanations for a transaction."""
    try:
        tx_doc = frappe.get_doc('Bank Transaction', transaction_name)
        
        engine = MatchingEngine()
        match_result = engine.find_matches({
            'amount': tx_doc.amount,
            'iban': tx_doc.iban,
            'reference': tx_doc.reference,
            'name': tx_doc.name
        })
        
        return {
            'status': 'success',
            'transaction': transaction_name,
            'account_status': match_result.get('status'),
            'account_info': match_result.get('account_info'),
            'matches': match_result.get('matches', [])
        }
    except Exception as e:
        frappe.log_error(str(e), "Match Suggestions Error")
        return {'status': 'error', 'message': str(e)}

@frappe.whitelist()
def manual_match_transaction(transaction_name, payment_name):
    """Manually match a transaction to a payment."""
    try:
        tx = frappe.get_doc('Bank Transaction', transaction_name)
        
        # Validate IBAN
        if not validate_iban(tx.iban):
            return {'status': 'error', 'message': 'Invalid IBAN format'}
        
        # Validate account is active
        if not is_account_active(tx.iban):
            return {'status': 'error', 'message': 'Associated bank account is not active'}
        
        # Calculate confidence for this specific match
        payment = frappe.get_doc('Payment Entry', payment_name)
        engine = MatchingEngine()
        
        confidence_result = engine.calculate_confidence({
            'amount': tx.amount,
            'iban': tx.iban,
            'reference': tx.reference,
            'name': tx.name
        }, {
            'paid_amount': payment.paid_amount,
            'party_bank_account': payment.party_bank_account,
            'reference_no': payment.reference_no,
            'party_name': payment.party_name
        })
        
        tx.matched_payment = payment_name
        tx.status = 'Manual Match'
        tx.confidence_score = 100  # User confirmed, full confidence
        tx.match_explanation = json.dumps({
            'type': 'manual',
            'matched_by': frappe.session.user,
            'components': confidence_result['explanation']
        })
        tx.save()
        
        return {
            'status': 'success',
            'message': 'Transaction manually matched',
            'confidence': confidence_result['score'],
            'explanation': confidence_result['explanation']
        }
    except Exception as e:
        frappe.log_error(str(e), "Manual Match Error")
        return {'status': 'error', 'message': str(e)}

@frappe.whitelist()
def get_transaction_explanation(transaction_name):
    """Get detailed explanation of why a transaction was matched."""
    try:
        tx = frappe.get_doc('Bank Transaction', transaction_name)
        if not tx.match_explanation:
            return {'status': 'not_matched', 'message': 'Transaction has no match explanation'}
        
        explanation = json.loads(tx.match_explanation)
        return {
            'status': 'success',
            'transaction': transaction_name,
            'score': tx.confidence_score,
            'matched_payment': tx.matched_payment,
            'explanation': explanation
        }
    except Exception as e:
        frappe.log_error(str(e), "Get Explanation Error")
        return {'status': 'error', 'message': str(e)}

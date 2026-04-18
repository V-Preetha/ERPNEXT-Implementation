import frappe
from banking_integration.services.matching_engine import MatchingEngine

def run_matching_engine():
    """Run matching engine for unmatched transactions."""
    transactions = frappe.get_all('Bank Transaction',
        filters={'status': 'Unmatched'},
        fields=['name'])

    engine = MatchingEngine()

    for tx_name in transactions:
        tx = frappe.get_doc('Bank Transaction', tx_name.name)
        matches = engine.find_matches(tx)

        # Update with suggestions (store in some way, perhaps custom field or log)
        if matches:
            tx.confidence_score = matches[0]['confidence']
            tx.save()
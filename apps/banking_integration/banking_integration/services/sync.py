import frappe
from banking_integration.services.ebics_service import EBICSService
from banking_integration.services.parser import parse_camt053
from banking_integration.services.matching_engine import MatchingEngine
from datetime import datetime, timedelta

def sync_bank_transactions():
    """Sync transactions for all active bank accounts."""
    bank_accounts = frappe.get_all('Bank Account', filters={'is_active': 1}, fields=['name'])

    for account in bank_accounts:
        try:
            sync_account_transactions(account.name)
        except Exception as e:
            frappe.log_error(f"Sync failed for {account.name}: {str(e)}", "Bank Sync Error")

def sync_account_transactions(bank_account_name):
    """Sync transactions for a specific bank account."""
    bank_account = frappe.get_doc('Bank Account', bank_account_name)
    ebics = EBICSService(bank_account)

    if not ebics.connect():
        raise Exception("EBICS connection failed")

    # Get last sync date
    from_date = bank_account.last_sync_date or (datetime.now() - timedelta(days=30)).date()
    to_date = datetime.now().date()

    xml_content = ebics.download_transactions(from_date, to_date)
    transactions = parse_camt053(xml_content)

    matching_engine = MatchingEngine()

    for tx_data in transactions:
        # Check for duplicate
        existing = frappe.get_all('Bank Transaction',
            filters={'transaction_id': tx_data['transaction_id']},
            fields=['name'])
        if existing:
            continue

        # Create transaction
        tx = frappe.get_doc({
            'doctype': 'Bank Transaction',
            'transaction_id': tx_data['transaction_id'],
            'bank_account': bank_account_name,
            'transaction_date': tx_data['transaction_date'],
            'value_date': tx_data['value_date'],
            'amount': tx_data['amount'],
            'currency': tx_data['currency'],
            'description': tx_data['description'],
            'reference': tx_data['reference'],
            'iban': tx_data['iban'],
            'name': tx_data['name']
        })

        # Detect chargeback
        if matching_engine.detect_chargeback(tx):
            tx.status = 'Chargeback'
            tx.chargeback_reason = 'Detected as chargeback'

        tx.insert()

        # Auto match
        match = matching_engine.auto_match(tx)
        if match:
            tx.matched_payment = match['payment']
            tx.confidence_score = match['confidence']
            tx.status = 'Matched'
            tx.save()

    # Update last sync
    bank_account.last_sync_date = to_date
    bank_account.save()
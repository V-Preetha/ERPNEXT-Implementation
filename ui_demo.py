from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Mock data for demonstration
BANK_ACCOUNTS = [
    {
        'name': 'DE001',
        'bank_name': 'Deutsche Bank',
        'iban': 'DE89370400440532013000',
        'status': 'Active',
        'last_sync_date': '2026-04-19',
        'company': 'Demo Company GmbH'
    },
    {
        'name': 'AT001',
        'bank_name': 'Bank Austria',
        'iban': 'AT611904300234573201',
        'status': 'Active',
        'last_sync_date': '2026-04-18',
        'company': 'Demo Company GmbH'
    },
    {
        'name': 'CH001',
        'bank_name': 'UBS Switzerland',
        'iban': 'CH21002300A1023502601',
        'status': 'Inactive',
        'last_sync_date': '2026-04-15',
        'company': 'Demo Company GmbH'
    }
]

BANK_TRANSACTIONS = [
    {
        'name': 'TXN001',
        'transaction_date': '2026-04-19',
        'amount': 1250.00,
        'reference': 'INV-2026-001',
        'iban': 'DE89370400440532013000',
        'status': 'Matched',
        'confidence_score': 99,
        'matched_payment': 'PAY-001'
    },
    {
        'name': 'TXN002',
        'transaction_date': '2026-04-18',
        'amount': -450.75,
        'reference': 'SUP-001',
        'iban': 'AT611904300234573201',
        'status': 'Matched',
        'confidence_score': 95,
        'matched_payment': 'PAY-002'
    },
    {
        'name': 'TXN003',
        'transaction_date': '2026-04-17',
        'amount': 3200.50,
        'reference': 'INV-2026-002',
        'iban': 'DE89370400440532013000',
        'status': 'Unmatched',
        'confidence_score': None,
        'matched_payment': None
    },
    {
        'name': 'TXN004',
        'transaction_date': '2026-04-16',
        'amount': -125.00,
        'reference': 'FEE-001',
        'iban': 'CH21002300A1023502601',
        'status': 'Chargeback',
        'confidence_score': None,
        'matched_payment': None
    }
]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/bank-accounts')
def bank_accounts():
    return render_template('bank_accounts.html', accounts=BANK_ACCOUNTS)

@app.route('/transactions')
def transactions():
    return render_template('transactions.html', transactions=BANK_TRANSACTIONS)

@app.route('/api/sync-account', methods=['POST'])
def sync_account():
    account_name = request.json.get('account_name')
    # Simulate sync operation
    return jsonify({
        'status': 'success',
        'message': f'Sync completed for {account_name}',
        'transactions_synced': 5
    })

@app.route('/api/run-matching', methods=['POST'])
def run_matching():
    # Simulate matching operation
    return jsonify({
        'status': 'success',
        'message': 'Matching engine completed',
        'transactions_matched': 3,
        'total_processed': 10
    })

@app.route('/api/manual-match', methods=['POST'])
def manual_match():
    transaction_name = request.json.get('transaction_name')
    payment_name = request.json.get('payment_name')
    # Simulate manual matching
    return jsonify({
        'status': 'success',
        'message': f'Transaction {transaction_name} matched to {payment_name}'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
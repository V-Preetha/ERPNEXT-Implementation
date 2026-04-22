from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from lxml import etree
import logging

app = Flask(__name__)

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.DEBUG)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.DEBUG)

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
        'account_name': 'DE001',
        'bank_name': 'Deutsche Bank',
        'status': 'Matched',
        'confidence_score': 95,
        'matched_payment': 'PAY-001',
        'explanation': {'amount_match': True, 'iban_match': True, 'reference_match': True}
    },
    {
        'name': 'TXN002',
        'transaction_date': '2026-04-18',
        'amount': 450.75,
        'reference': 'SUP-001',
        'iban': 'AT611904300234573201',
        'account_name': 'AT001',
        'bank_name': 'Bank Austria',
        'status': 'Matched',
        'confidence_score': 92,
        'matched_payment': 'PAY-002',
        'explanation': {'amount_match': True, 'iban_match': True, 'reference_match': False}
    },
    {
        'name': 'TXN003',
        'transaction_date': '2026-04-17',
        'amount': 3200.50,
        'reference': 'INV-2026-002',
        'iban': 'DE89370400440532013000',
        'account_name': 'DE001',
        'bank_name': 'Deutsche Bank',
        'status': 'Unmatched',
        'confidence_score': None,
        'matched_payment': None,
        'explanation': None
    },
    {
        'name': 'TXN004',
        'transaction_date': '2026-04-16',
        'amount': 125.00,
        'reference': 'FEE-001',
        'iban': 'CH21002300A1023502601',
        'account_name': 'CH001',
        'bank_name': 'UBS Switzerland',
        'status': 'Inactive Account',
        'confidence_score': 0,
        'matched_payment': None,
        'explanation': {'reason': 'Inactive Account'}
    }
]

# ==================== VALIDATION & MATCHING HELPERS ====================

def get_bank_account_by_iban(iban):
    """Retrieve bank account by IBAN."""
    for account in BANK_ACCOUNTS:
        if account['iban'] == iban:
            return account
    return None

def is_account_active(iban):
    """Check if bank account is active."""
    account = get_bank_account_by_iban(iban)
    return account and account.get('status') == 'Active' if account else False

def validate_transaction(transaction):
    """Validate transaction before matching.
    
    Returns:
        {
            'valid': bool,
            'status': str,
            'account': dict or None,
            'account_name': str,
            'bank_name': str
        }
    """
    iban = transaction.get('iban', '')
    
    account = get_bank_account_by_iban(iban)
    if not account:
        return {
            'valid': False,
            'status': 'Invalid IBAN',
            'account': None,
            'account_name': 'Unknown',
            'bank_name': 'Unknown'
        }
    
    if account.get('status') != 'Active':
        return {
            'valid': False,
            'status': 'Inactive Account',
            'account': account,
            'account_name': account.get('name'),
            'bank_name': account.get('bank_name')
        }
    
    return {
        'valid': True,
        'status': 'Valid',
        'account': account,
        'account_name': account.get('name'),
        'bank_name': account.get('bank_name')
    }

def calculate_match_score(transaction, invoice):
    """Calculate match score with component breakdown.
    
    Returns:
        {
            'score': 0.0-1.0 (rounded to 2 decimals),
            'confidence': 0-100 (as integer),
            'explanation': dict with each component
        }
    """
    score = 0.0
    explanation = {
        'amount_match': False,
        'amount_reason': 'Amount mismatch',
        'iban_match': False,
        'iban_reason': 'IBAN not provided',
        'reference_match': False,
        'reference_reason': 'Reference not provided',
        'name_match': False,
        'name_reason': 'Name not provided'
    }
    
    # Amount match (40%)
    if abs(float(transaction.get('amount', 0)) - float(invoice.get('amount', 0))) < 0.01:
        score += 0.40
        explanation['amount_match'] = True
        explanation['amount_reason'] = 'Exact match'
    
    # IBAN match (30%)
    if transaction.get('iban') == invoice.get('iban'):
        score += 0.30
        explanation['iban_match'] = True
        explanation['iban_reason'] = 'Exact match'
    
    # Reference match (20%)
    trans_ref = str(transaction.get('reference', '')).lower()
    inv_ref = str(invoice.get('reference', '')).lower()
    if trans_ref and inv_ref and trans_ref in inv_ref or inv_ref in trans_ref:
        score += 0.20
        explanation['reference_match'] = True
        explanation['reference_reason'] = 'Partial match'
    
    # Round score to 2 decimal places
    score = round(score, 2)
    confidence = int(round(score * 100))
    
    return {
        'score': score,
        'confidence': confidence,
        'explanation': explanation
    }

# ==================== MOCK INVOICES FOR MATCHING ====================
MOCK_INVOICES = [
    {
        'name': 'PAY-001',
        'amount': 1250.00,
        'iban': 'DE89370400440532013000',
        'reference': 'INV-2026-001'
    },
    {
        'name': 'PAY-002',
        'amount': 450.75,
        'iban': 'AT611904300234573201',
        'reference': 'SUP-001'
    },
    {
        'name': 'PAY-003',
        'amount': 3200.50,
        'iban': 'DE89370400440532013000',
        'reference': 'INV-2026-002'
    }
]

# ==================== ROUTES ====================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/bank-accounts')
def bank_accounts():
    return render_template('bank_accounts.html', accounts=BANK_ACCOUNTS)

@app.route('/transactions')
def transactions():
    return render_template('transactions.html', transactions=BANK_TRANSACTIONS)

@app.route('/payments')
def payments():
    return render_template('payments.html')

@app.route('/api/sync-account', methods=['POST'])
def sync_account():
    account_name = request.json.get('account_name')
    account = next((acct for acct in BANK_ACCOUNTS if acct['name'] == account_name), None)
    if not account:
        return jsonify({
            'status': 'error',
            'message': f'Bank account {account_name} not found'
        }), 404

    today = datetime.today().strftime('%Y-%m-%d')
    account['last_sync_date'] = today

    # Simulate adding new transactions for the synced account
    new_transaction = {
        'name': f'TXN{len(BANK_TRANSACTIONS) + 1:03d}',
        'transaction_date': today,
        'amount': 250.00,
        'reference': 'Auto Synced Transaction',
        'iban': account['iban'],
        'account_name': account['name'],
        'bank_name': account['bank_name'],
        'status': 'Unmatched',
        'confidence_score': 0,
        'matched_payment': None,
        'explanation': None
    }
    BANK_TRANSACTIONS.append(new_transaction)

    return jsonify({
        'status': 'success',
        'message': f'Sync completed for {account_name}',
        'transactions_synced': 1,
        'new_transaction': new_transaction
    })

@app.route('/api/run-matching', methods=['POST'])
def run_matching():
    """Run matching engine with validation."""
    results = {
        'matched': 0,
        'review': 0,
        'invalid_iban': 0,
        'inactive_account': 0,
        'unmatched': 0,
        'details': []
    }

    for transaction in BANK_TRANSACTIONS:
        # Skip if already manually matched
        if transaction.get('status') == 'Manual Match':
            continue
        
        # Validate transaction
        validation = validate_transaction(transaction)
        if not validation['valid']:
            transaction['status'] = validation['status']
            transaction['confidence_score'] = 0
            transaction['account_name'] = validation['account_name']
            transaction['bank_name'] = validation['bank_name']
            transaction['explanation'] = {'reason': validation['status']}
            results[validation['status'].lower().replace(' ', '_')] += 1
            results['details'].append({
                'transaction': transaction['name'],
                'status': validation['status']
            })
            continue
        
        # Set account info
        transaction['account_name'] = validation['account_name']
        transaction['bank_name'] = validation['bank_name']
        
        # Try to find matches
        best_match = None
        best_confidence = 0
        best_explanation = {}
        
        for invoice in MOCK_INVOICES:
            result = calculate_match_score(transaction, invoice)
            if result['confidence'] > best_confidence:
                best_confidence = result['confidence']
                best_explanation = result['explanation']
                best_match = invoice
        
        # Ensure confidence is always assigned
        if best_match is None:
            best_confidence = 0
        
        # Assign status based on confidence
        if best_confidence >= 90:
            transaction['status'] = 'Matched'
            transaction['matched_payment'] = best_match['name']
            transaction['confidence_score'] = best_confidence
            transaction['explanation'] = best_explanation
            results['matched'] += 1
        elif best_confidence >= 50:
            transaction['status'] = 'Review'
            transaction['matched_payment'] = best_match['name'] if best_match else None
            transaction['confidence_score'] = best_confidence
            transaction['explanation'] = best_explanation
            results['review'] += 1
        else:
            transaction['status'] = 'Unmatched'
            transaction['matched_payment'] = None
            transaction['confidence_score'] = best_confidence
            transaction['explanation'] = best_explanation
            results['unmatched'] += 1
        
        results['details'].append({
            'transaction': transaction['name'],
            'status': transaction['status'],
            'confidence': transaction['confidence_score']
        })

    return jsonify({
        'status': 'success',
        'message': 'Matching engine completed',
        'results': results
    })

@app.route('/api/manual-match', methods=['POST'])
def manual_match():
    transaction_name = request.json.get('transaction_name')
    payment_name = request.json.get('payment_name')
    transaction = next((tx for tx in BANK_TRANSACTIONS if tx['name'] == transaction_name), None)

    if not transaction:
        return jsonify({
            'status': 'error',
            'message': f'Transaction {transaction_name} not found'
        }), 404

    # Validate before manual match
    validation = validate_transaction(transaction)
    if not validation['valid']:
        return jsonify({
            'status': 'error',
            'message': f'Cannot match: {validation["status"]}'
        }), 400
    
    transaction['account_name'] = validation['account_name']
    transaction['bank_name'] = validation['bank_name']
    transaction['status'] = 'Manual Match'
    transaction['matched_payment'] = payment_name
    transaction['confidence_score'] = 100
    transaction['explanation'] = {'reason': 'User confirmed match'}

    return jsonify({
        'status': 'success',
        'message': f'Transaction {transaction_name} matched to {payment_name}',
        'transaction': transaction
    })

@app.route('/api/get-explanation', methods=['POST'])
def get_explanation():
    """Get detailed explanation for a transaction match."""
    transaction_name = request.json.get('transaction_name')
    transaction = next((tx for tx in BANK_TRANSACTIONS if tx['name'] == transaction_name), None)
    
    if not transaction:
        return jsonify({
            'status': 'error',
            'message': f'Transaction {transaction_name} not found'
        }), 404
    
    if not transaction.get('explanation'):
        return jsonify({
            'status': 'error',
            'message': 'No explanation available'
        }), 400
    
    return jsonify({
        'status': 'success',
        'transaction': transaction_name,
        'confidence': transaction.get('confidence_score'),
        'matched_payment': transaction.get('matched_payment'),
        'explanation': transaction.get('explanation'),
        'account_name': transaction.get('account_name'),
        'bank_name': transaction.get('bank_name')
    })

@app.route('/api/add-bank-account', methods=['POST'])
def add_bank_account():
    data = request.json
    new_account = {
        'name': data.get('name', f'ACCT{len(BANK_ACCOUNTS) + 1:03d}'),
        'bank_name': data.get('bank_name', 'Demo Bank'),
        'iban': data.get('iban', 'N/A'),
        'status': data.get('status', 'Active'),
        'last_sync_date': data.get('last_sync_date', None),
        'company': data.get('company', 'Demo Company GmbH')
    }
    BANK_ACCOUNTS.append(new_account)
    return jsonify({
        'status': 'success',
        'message': f'Bank account {new_account["name"]} added',
        'account': new_account
    })

@app.route('/api/add-transaction', methods=['POST'])
def add_transaction():
    data = request.json
    new_transaction = {
        'name': data.get('name', f'TXN{len(BANK_TRANSACTIONS) + 1:03d}'),
        'transaction_date': data.get('transaction_date', datetime.today().strftime('%Y-%m-%d')),
        'amount': float(data.get('amount', 0)),
        'reference': data.get('reference', ''),
        'iban': data.get('iban', ''),
        'account_name': 'Unknown',
        'bank_name': 'Unknown',
        'status': data.get('status', 'Unmatched'),
        'confidence_score': 0,
        'matched_payment': data.get('matched_payment', None),
        'explanation': None
    }
    BANK_TRANSACTIONS.append(new_transaction)
    return jsonify({
        'status': 'success',
        'message': f'Transaction {new_transaction["name"]} added',
        'transaction': new_transaction
    })

def generate_pain001(creditor_name, creditor_iban, creditor_bic, debtor_name, debtor_iban, debtor_bic, amount, reference, execution_date):
    """Generate SEPA pain.001.001.03 XML for credit transfer"""
    print(f"Generating XML for {creditor_name} -> {debtor_name}, amount: {amount}")
    ns = 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03'
    
    # Create the root element with the default namespace
    root = etree.Element('Document', nsmap={None: ns})
    cstmr_cdt_trf_initn = etree.SubElement(root, 'CstmrCdtTrfInitn')
    
    # Group header
    grp_hdr = etree.SubElement(cstmr_cdt_trf_initn, 'GrpHdr')
    etree.SubElement(grp_hdr, 'MsgId').text = f'MSG-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    etree.SubElement(grp_hdr, 'CreDtTm').text = datetime.now().isoformat()
    etree.SubElement(grp_hdr, 'NbOfTxs').text = '1'
    etree.SubElement(grp_hdr, 'CtrlSum').text = f'{amount:.2f}'
    initg_pty = etree.SubElement(grp_hdr, 'InitgPty')
    etree.SubElement(initg_pty, 'Nm').text = creditor_name
    
    # Payment information
    pmt_inf = etree.SubElement(cstmr_cdt_trf_initn, 'PmtInf')
    etree.SubElement(pmt_inf, 'PmtInfId').text = f'PMT-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    etree.SubElement(pmt_inf, 'PmtMtd').text = 'TRF'
    etree.SubElement(pmt_inf, 'BtchBookg').text = 'true'
    etree.SubElement(pmt_inf, 'NbOfTxs').text = '1'
    etree.SubElement(pmt_inf, 'CtrlSum').text = f'{amount:.2f}'
    
    # Payment type information
    pmt_tp_inf = etree.SubElement(pmt_inf, 'PmtTpInf')
    svc_lvl = etree.SubElement(pmt_tp_inf, 'SvcLvl')
    etree.SubElement(svc_lvl, 'Cd').text = 'SEPA'
    
    etree.SubElement(pmt_inf, 'ReqdExctnDt').text = execution_date
    
    # Debtor information
    dbtr = etree.SubElement(pmt_inf, 'Dbtr')
    etree.SubElement(dbtr, 'Nm').text = debtor_name
    
    # Debtor account
    dbtr_acct = etree.SubElement(pmt_inf, 'DbtrAcct')
    id_elem = etree.SubElement(dbtr_acct, 'Id')
    etree.SubElement(id_elem, 'IBAN').text = debtor_iban
    
    # Debtor agent
    dbtr_agt = etree.SubElement(pmt_inf, 'DbtrAgt')
    fin_instn_id = etree.SubElement(dbtr_agt, 'FinInstnId')
    etree.SubElement(fin_instn_id, 'BIC').text = debtor_bic
    
    # Credit transfer transaction information
    cdt_trf_tx_inf = etree.SubElement(pmt_inf, 'CdtTrfTxInf')
    pmt_id = etree.SubElement(cdt_trf_tx_inf, 'PmtId')
    etree.SubElement(pmt_id, 'EndToEndId').text = f'END-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    
    amt = etree.SubElement(cdt_trf_tx_inf, 'Amt')
    instd_amt = etree.SubElement(amt, 'InstdAmt')
    instd_amt.text = f'{amount:.2f}'
    instd_amt.set('Ccy', 'EUR')
    
    # Creditor agent
    cdtr_agt = etree.SubElement(cdt_trf_tx_inf, 'CdtrAgt')
    fin_instn_id_cdtr = etree.SubElement(cdtr_agt, 'FinInstnId')
    etree.SubElement(fin_instn_id_cdtr, 'BIC').text = creditor_bic
    
    # Creditor
    cdtr = etree.SubElement(cdt_trf_tx_inf, 'Cdtr')
    etree.SubElement(cdtr, 'Nm').text = creditor_name
    
    # Creditor account
    cdtr_acct = etree.SubElement(cdt_trf_tx_inf, 'CdtrAcct')
    id_elem_cdtr = etree.SubElement(cdtr_acct, 'Id')
    etree.SubElement(id_elem_cdtr, 'IBAN').text = creditor_iban
    
    # Remittance information
    rmt_inf = etree.SubElement(cdt_trf_tx_inf, 'RmtInf')
    etree.SubElement(rmt_inf, 'Ustrd').text = reference
    
    xml_content = etree.tostring(root, encoding='unicode', pretty_print=True)
    print(f"XML generated, length: {len(xml_content)}")
    return xml_content

@app.route('/api/edit-bank-account', methods=['POST'])
def edit_bank_account():
    data = request.json
    original_name = data.get('original_name')
    new_name = data.get('name', original_name)

    # Find and update the account
    for account in BANK_ACCOUNTS:
        if account['name'] == original_name:
            account.update({
                'name': new_name,
                'bank_name': data.get('bank_name', account['bank_name']),
                'iban': data.get('iban', account['iban']),
                'status': data.get('status', account['status']),
                'last_sync_date': data.get('last_sync_date', account['last_sync_date']),
                'company': data.get('company', account['company'])
            })
            return jsonify({
                'status': 'success',
                'message': f'Bank account {original_name} updated',
                'account': account
            })
    
    return jsonify({
        'status': 'error',
        'message': f'Bank account {original_name} not found'
    }), 404

@app.route('/api/generate-sepa-payment', methods=['POST'])
def generate_sepa_payment():
    print("SEPA API called")
    data = request.json
    print(f"Received data: {data}")
    
    creditor_name = data.get('creditor_name')
    creditor_iban = data.get('creditor_iban')
    creditor_bic = data.get('creditor_bic')
    debtor_name = data.get('debtor_name')
    debtor_iban = data.get('debtor_iban')
    debtor_bic = data.get('debtor_bic')
    amount = float(data.get('amount', 0))
    reference = data.get('reference')
    execution_date = data.get('execution_date')
    
    print(f"Parsed data: creditor={creditor_name}, amount={amount}")
    
    if not all([creditor_name, creditor_iban, creditor_bic, debtor_name, debtor_iban, debtor_bic, amount, reference, execution_date]):
        print("Missing required fields")
        return jsonify({
            'status': 'error',
            'message': 'All fields are required'
        }), 400
    
    try:
        xml_content = generate_pain001(creditor_name, creditor_iban, creditor_bic, debtor_name, debtor_iban, debtor_bic, amount, reference, execution_date)
        print(f"XML generated, length: {len(xml_content)}")
        return jsonify({
            'status': 'success',
            'message': 'SEPA payment XML generated',
            'xml': xml_content
        })
    except Exception as e:
        print(f"Error generating XML: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error generating XML: {str(e)}'
        }), 500

# ==================== PAYMENTS API ROUTES ====================

@app.route('/api/method/banking_integration.api.payments.get_payments', methods=['GET', 'POST'])
def get_payments():
    """Get all payments for the demo."""
    # Convert mock invoices to payment format
    payments = []
    for invoice in MOCK_INVOICES:
        payment = {
            'payment_id': invoice['name'],
            'amount': invoice['amount'],
            'reference': invoice['reference'],
            'iban': invoice['iban'],
            'bank_account': 'DE001',  # Default bank account
            'status': 'Completed',
            'created_at': '2026-04-20T10:00:00Z',
            'transaction_id': None
        }
        payments.append(payment)
    
    return jsonify({
        'message': {
            'status': 'success',
            'payments': payments
        }
    })

@app.route('/api/method/banking_integration.api.payments.get_payment_details', methods=['POST'])
def get_payment_details():
    """Get details for a specific payment."""
    payment_id = request.json.get('payment_id')
    
    # Find the payment in mock invoices
    payment = None
    for invoice in MOCK_INVOICES:
        if invoice['name'] == payment_id:
            payment = {
                'payment_id': invoice['name'],
                'amount': invoice['amount'],
                'reference': invoice['reference'],
                'iban': invoice['iban'],
                'bank_account': 'DE001',
                'status': 'Completed',
                'created_at': '2026-04-20T10:00:00Z',
                'transaction_id': None
            }
            break
    
    if not payment:
        return jsonify({
            'message': {
                'status': 'error',
                'message': f'Payment {payment_id} not found'
            }
        }), 404
    
    return jsonify({
        'message': {
            'status': 'success',
            'payment': payment
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
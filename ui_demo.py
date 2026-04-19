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
        'reference': f'SYNC-{account_name}-{today}',
        'iban': account['iban'],
        'status': 'Unmatched',
        'confidence_score': None,
        'matched_payment': None
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
    unmatched = [tx for tx in BANK_TRANSACTIONS if tx['status'] == 'Unmatched']
    matched_count = 0
    mock_payments = ['PAY-003', 'PAY-004', 'PAY-005', 'PAY-006']

    for index, transaction in enumerate(unmatched):
        if matched_count >= len(mock_payments):
            break
        transaction['status'] = 'Matched'
        transaction['matched_payment'] = mock_payments[index]
        transaction['confidence_score'] = 92
        matched_count += 1

    return jsonify({
        'status': 'success',
        'message': f'Matching engine completed: {matched_count} transactions matched',
        'transactions_matched': matched_count,
        'total_processed': len(unmatched)
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

    transaction['status'] = 'Manual Match'
    transaction['matched_payment'] = payment_name
    transaction['confidence_score'] = 100

    return jsonify({
        'status': 'success',
        'message': f'Transaction {transaction_name} matched to {payment_name}',
        'transaction': transaction
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
        'status': data.get('status', 'Unmatched'),
        'confidence_score': None,
        'matched_payment': data.get('matched_payment', None)
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
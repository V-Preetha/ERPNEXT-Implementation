import requests
import json

# Test edit-bank-account API
url = 'http://127.0.0.1:5000/api/edit-bank-account'
data = {
    'name': 'DE001',
    'bank_name': 'Updated Deutsche Bank',
    'iban': 'DE89370400440532013000',
    'status': 'Active',
    'last_sync_date': '2026-04-20',
    'company': 'Demo Company GmbH'
}
try:
    response = requests.post(url, json=data, timeout=5)
    print('Edit Bank Account Response:')
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f'Error: {e}')
print()

# Test generate-sepa-payment API
url = 'http://127.0.0.1:5000/api/generate-sepa-payment'
data = {
    'creditor_name': 'Demo Company GmbH',
    'creditor_iban': 'DE89370400440532013000',
    'creditor_bic': 'DEUTDEFF',
    'debtor_name': 'Supplier GmbH',
    'debtor_iban': 'AT611904300234573201',
    'debtor_bic': 'BKAUATWW',
    'amount': 1250.00,
    'reference': 'INV-2026-001',
    'execution_date': '2026-04-21'
}
try:
    response = requests.post(url, json=data, timeout=5)
    print('Generate SEPA Payment Response:')
    result = response.json()
    print(f'Status: {result.get("status")}')
    print(f'Message: {result.get("message")}')
    if 'xml' in result:
        print('XML generated successfully (length:', len(result['xml']), 'characters)')
        print('First 500 characters of XML:')
        print(result['xml'][:500])
except Exception as e:
    print(f'Error: {e}')
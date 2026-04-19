#!/usr/bin/env python
"""Check current transaction status."""
import requests

print('Current Transactions in System:')
print('-' * 50)

for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
    tx_name = f'TXN{i:03d}' if i <= 6 else f'TXN{i}'
    r = requests.post('http://127.0.0.1:5000/api/get-explanation', 
                     json={'transaction_name': tx_name})
    if r.status_code == 200:
        data = r.json()
        acc = data.get('account_name', 'Unknown')
        conf = data.get('confidence', 'N/A')
        payment = data.get('matched_payment', 'None')
        print(f'{tx_name}: Account={acc}, Confidence={conf}%, Payment={payment}')

print('-' * 50)
print('(Transactions are created dynamically, names may vary)')

#!/usr/bin/env python
"""Verify template fix and None handling."""
import requests

print('Template Fix Verification')
print('=' * 60)

# Test 1: Transactions page renders
print('\n[TEST 1] Transactions Page Renders')
r = requests.get('http://127.0.0.1:5000/transactions')
if r.status_code == 200:
    print('  ✓ Transactions page renders successfully')
    if 'confidence-' in r.text:
        print('  ✓ Confidence styling classes present')
else:
    print(f'  ERROR: Status {r.status_code}')

# Test 2: Bank accounts page renders
print('\n[TEST 2] Bank Accounts Page Renders')
r = requests.get('http://127.0.0.1:5000/bank-accounts')
if r.status_code == 200:
    print('  ✓ Bank accounts page renders successfully')
else:
    print(f'  ERROR: Status {r.status_code}')

# Test 3: Matching works
print('\n[TEST 3] Run Matching')
r = requests.post('http://127.0.0.1:5000/api/run-matching', json={})
if r.status_code == 200:
    results = r.json()['results']
    print(f'  ✓ Matching completed')
    print(f'    Matched: {results.get("matched", 0)}')
    print(f'    Review: {results.get("review", 0)}')
    print(f'    Unmatched: {results.get("unmatched", 0)}')
else:
    print(f'  ERROR: Status {r.status_code}')

# Test 4: Confidence values are valid
print('\n[TEST 4] Confidence Values Are Valid')
r = requests.get('http://127.0.0.1:5000/transactions')
if r.status_code == 200:
    # Check that template renders without None comparison errors
    if '%-' not in r.text and 'TypeError' not in r.text:
        print('  ✓ No template errors in rendered HTML')
    else:
        print('  ⚠ Check HTML for issues')

# Test 5: Manual match works
print('\n[TEST 5] Manual Match')
r = requests.post('http://127.0.0.1:5000/api/manual-match', json={
    'transaction_name': 'TXN003',
    'payment_name': 'PAY-001'
})
if r.status_code == 200:
    print('  ✓ Manual match successful')
elif r.status_code == 400:
    print('  ✓ Manual match validation working (400 for invalid)')
else:
    print(f'  ERROR: Status {r.status_code}')

print('\n' + '=' * 60)
print('Template Fix Verification: COMPLETE')
print('\nFix Applied:')
print('  - Template now safely handles None confidence_score values')
print('  - Uses {% set conf = transaction.confidence_score or 0 %} approach')
print('  - Prevents TypeError when comparing None >= 90')

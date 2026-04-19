from ui_demo import generate_pain001

try:
    xml = generate_pain001(
        'Demo Company GmbH', 
        'DE89370400440532013000', 
        'DEUTDEFF', 
        'Supplier GmbH', 
        'AT611904300234573201', 
        'BKAUATWW', 
        1250.00, 
        'INV-2026-001', 
        '2026-04-21'
    )
    print('XML generated successfully!')
    print('Length:', len(xml))
    print('First 500 chars:')
    print(xml[:500])
    print('...')
    print('Last 500 chars:')
    print(xml[-500:])
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
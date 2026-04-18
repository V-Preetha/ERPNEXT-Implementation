#!/usr/bin/env python3
"""
Demo script for Banking Integration App
This script demonstrates the key functionality without requiring full Frappe setup
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'banking_integration'))

# Mock frappe module for demonstration
class MockFrappe:
    class db:
        @staticmethod
        def get_all(*args, **kwargs):
            return []

    class get_doc:
        def __init__(self, doctype, name=None):
            self.doctype = doctype
            self.name = name

    @staticmethod
    def get_all(*args, **kwargs):
        return []

    @staticmethod
    def log_error(message, title=None):
        print(f"ERROR: {title} - {message}")

    @staticmethod
    def get_site_config():
        # Use a proper Fernet key for demo
        return {'encryption_key': 'XBtpBws0WJfoJB7dAbuSvtdNovIEinIZfmaxtgPU2_M='}

    @staticmethod
    def conf():
        return {'encryption_key': 'XBtpBws0WJfoJB7dAbuSvtdNovIEinIZfmaxtgPU2_M='}

    class utils:
        @staticmethod
        def nowdate():
            from datetime import date
            return date.today().isoformat()

# Mock frappe
sys.modules['frappe'] = MockFrappe()
sys.modules['frappe.model'] = type('module', (), {})()
sys.modules['frappe.model.document'] = type('module', (), {'Document': object})()

def demo_xml_parsing():
    """Demonstrate camt.053 XML parsing"""
    print("=== XML Parsing Demo ===")

    from banking_integration.services.parser import parse_camt053

    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
        <BkToCstmrStmt>
            <Stmt>
                <Id>12345</Id>
                <CreDtTm>2023-01-01T00:00:00</CreDtTm>
                <Acct>
                    <Id>
                        <IBAN>DE12345678901234567890</IBAN>
                    </Id>
                </Acct>
                <Ntry>
                    <Amt Ccy="EUR">100.00</Amt>
                    <CdtDbtInd>CRDT</CdtDbtInd>
                    <BookgDt>
                        <Dt>2023-01-01</Dt>
                    </BookgDt>
                    <ValDt>
                        <Dt>2023-01-01</Dt>
                    </ValDt>
                    <NtryDtls>
                        <TxDtls>
                            <Refs>
                                <EndToEndId>INV001</EndToEndId>
                            </Refs>
                            <RltdPties>
                                <Dbtr>
                                    <Nm>Customer Name</Nm>
                                </Dbtr>
                            </RltdPties>
                        </TxDtls>
                    </NtryDtls>
                </Ntry>
            </Stmt>
        </BkToCstmrStmt>
    </Document>"""

    transactions = parse_camt053(sample_xml)
    print(f"Parsed {len(transactions)} transactions:")
    for tx in transactions:
        print(f"  - ID: {tx['transaction_id']}, Amount: {tx['amount']} {tx['currency']}, Reference: {tx['reference']}")

def demo_xml_generation():
    """Demonstrate pain.001 XML generation"""
    print("\n=== XML Generation Demo ===")

    from banking_integration.services.xml_generator import generate_pain001

    payment_data = {
        'message_id': 'MSG001',
        'payment_info_id': 'PMT001',
        'amount': 100.00,
        'execution_date': '2023-01-01',
        'debtor_name': 'Test Company',
        'debtor_iban': 'DE12345678901234567890',
        'creditor_name': 'Supplier GmbH',
        'creditor_iban': 'DE09876543210987654321',
        'end_to_end_id': 'E2E001',
        'remittance_info': 'Invoice payment'
    }

    xml_content = generate_pain001(payment_data)
    print("Generated pain.001 XML:")
    print(xml_content[:500] + "..." if len(xml_content) > 500 else xml_content)

def demo_matching_engine():
    """Demonstrate matching engine"""
    print("\n=== Matching Engine Demo ===")

    from banking_integration.services.matching_engine import MatchingEngine

    engine = MatchingEngine()

    # Mock transaction
    class MockTransaction:
        def __init__(self, amount, iban, reference, name):
            self.amount = amount
            self.iban = iban
            self.reference = reference
            self.name = name

    # Mock payment
    class MockPayment:
        def __init__(self, paid_amount, party_bank_account, reference_no, party_name):
            self.paid_amount = paid_amount
            self.party_bank_account = party_bank_account
            self.reference_no = reference_no
            self.party_name = party_name

    transaction = MockTransaction(100.00, 'DE12345678901234567890', 'INV001', 'Test Customer')
    payment = MockPayment(100.00, 'DE12345678901234567890', 'INV001', 'Test Customer')

    confidence = engine.calculate_confidence(transaction, payment)
    print(f"Matching confidence: {confidence}%")

    # Test different scenarios
    scenarios = [
        ("Exact match", 100.00, 'DE12345678901234567890', 'INV001', 'Test Customer'),
        ("Amount mismatch", 95.00, 'DE12345678901234567890', 'INV001', 'Test Customer'),
        ("IBAN mismatch", 100.00, 'DE99999999999999999999', 'INV001', 'Test Customer'),
        ("Reference mismatch", 100.00, 'DE12345678901234567890', 'INV999', 'Test Customer'),
    ]

    print("\nConfidence scores for different scenarios:")
    for desc, amt, iban, ref, name in scenarios:
        tx = MockTransaction(amt, iban, ref, name)
        score = engine.calculate_confidence(tx, payment)
        print(f"  {desc}: {score}%")

def demo_encryption():
    """Demonstrate encryption functionality"""
    print("\n=== Encryption Demo ===")

    from banking_integration.utils.encryption import encrypt_password, decrypt_password

    password = "test_ebics_password_123"
    print(f"Original password: {password}")

    encrypted = encrypt_password(password)
    print(f"Encrypted: {encrypted}")

    decrypted = decrypt_password(encrypted)
    print(f"Decrypted: {decrypted}")

    print(f"Decryption successful: {password == decrypted}")

def main():
    """Run all demos"""
    print("Banking Integration App - Demo")
    print("=" * 40)

    try:
        demo_xml_parsing()
        demo_xml_generation()
        demo_matching_engine()
        demo_encryption()

        print("\n=== Demo Complete ===")
        print("All core functionalities demonstrated successfully!")
        print("\nTo run in production:")
        print("1. Install Frappe/ERPNext")
        print("2. Install the banking_integration app")
        print("3. Configure bank accounts and EBICS credentials")
        print("4. Run scheduler jobs for automated operations")

    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
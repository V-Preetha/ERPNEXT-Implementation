import frappe
from frappe import _
from banking_integration.services.xml_generator import generate_pain001
from banking_integration.services.ebics_service import EBICSService

@frappe.whitelist()
def generate_sepa_payment(invoice_name):
    """Generate SEPA payment for an invoice."""
    try:
        invoice = frappe.get_doc('Purchase Invoice', invoice_name)
        if invoice.outstanding_amount <= 0:
            frappe.throw(_("Invoice is fully paid"))

        # Get bank account
        bank_account = frappe.get_all('Bank Account', filters={'company': invoice.company, 'is_active': 1}, fields=['name'])[0]
        bank_account_doc = frappe.get_doc('Bank Account', bank_account.name)

        payment_data = {
            'message_id': f"MSG_{invoice.name}",
            'payment_info_id': f"PMT_{invoice.name}",
            'amount': invoice.outstanding_amount,
            'execution_date': (frappe.utils.nowdate()),
            'debtor_name': invoice.company,
            'debtor_iban': bank_account_doc.iban,
            'creditor_name': invoice.supplier_name,
            'creditor_iban': invoice.supplier_bank_account or '',
            'end_to_end_id': invoice.name,
            'remittance_info': f"Invoice {invoice.name}"
        }

        xml_content = generate_pain001(payment_data)

        # In real, upload via EBICS
        ebics = EBICSService(bank_account_doc)
        ebics.upload_payment(xml_content)

        return {'status': 'success', 'xml': xml_content}
    except Exception as e:
        frappe.log_error(str(e), "SEPA Payment Error")
        return {'status': 'error', 'message': str(e)}

@frappe.whitelist()
def on_payment_submit(doc, method):
    """Hook on payment submit."""
    # Link to bank transaction if applicable
    pass

@frappe.whitelist()
def on_payment_cancel(doc, method):
    """Hook on payment cancel."""
    # Unlink bank transaction
    pass
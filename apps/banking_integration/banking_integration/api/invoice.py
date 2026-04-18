import frappe

@frappe.whitelist()
def on_invoice_submit(doc, method):
    """Hook on invoice submit."""
    # Mark for payment matching
    pass
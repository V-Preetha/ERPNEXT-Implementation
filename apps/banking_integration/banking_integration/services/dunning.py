import frappe
from datetime import datetime, timedelta

def trigger_dunning():
    """Trigger dunning for overdue invoices."""
    # Get overdue invoices
    overdue_invoices = frappe.get_all('Purchase Invoice',
        filters={
            'docstatus': 1,
            'outstanding_amount': ['>', 0],
            'due_date': ['<', datetime.now().date()]
        },
        fields=['name', 'outstanding_amount', 'due_date'])

    for invoice in overdue_invoices:
        # Create dunning entry or send notification
        frappe.logger().info(f"Dunning triggered for invoice {invoice.name}")
        # In real implementation, create Dunning DocType or send email
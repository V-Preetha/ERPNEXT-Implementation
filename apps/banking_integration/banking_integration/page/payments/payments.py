import frappe
from frappe import _

def get_context(context):
    context.title = _("Payments")
    # Payments data will be loaded via API

app_name = "banking_integration"
app_title = "Banking Integration"
app_publisher = "Spazorlabs"
app_description = "EBICS Banking Integration for ERPNext"
app_icon = "octicon octicon-credit-card"
app_color = "blue"
app_email = "info@spazorlabs.com"
app_license = "MIT"

# Document Events
doc_events = {
    "Payment Entry": {
        "on_submit": "banking_integration.api.payment.on_payment_submit",
        "on_cancel": "banking_integration.api.payment.on_payment_cancel",
    },
    "Purchase Invoice": {
        "on_submit": "banking_integration.api.invoice.on_invoice_submit",
    },
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "banking_integration.services.sync.sync_bank_transactions",
    ],
    "hourly": [
        "banking_integration.services.matching.run_matching_engine",
    ],
    "weekly": [
        "banking_integration.services.dunning.trigger_dunning",
    ],
}

# User Data Protection
user_data_fields = [
    {
        "doctype": "Bank Account",
        "filter_by": "owner",
        "redact_fields": ["iban", "account_number"],
        "partial": 1,
    },
]
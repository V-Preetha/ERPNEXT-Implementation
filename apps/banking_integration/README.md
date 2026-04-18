# Banking Integration for ERPNext

A comprehensive EBICS (Electronic Banking Internet Communication Standard) banking integration app for ERPNext, enabling seamless bank account connectivity, transaction synchronization, automated payment matching, and SEPA payment generation.

## Description

This Frappe app provides enterprise-grade banking integration for ERPNext, allowing businesses to connect their bank accounts securely via EBICS protocol. It automates the reconciliation process by syncing bank transactions, matching them to payments and invoices using intelligent algorithms, and generating SEPA payments for outstanding invoices.

The app is designed for production use with features like idempotent syncing, audit logging, chargeback detection, and secure credential management.

## Features

### Core Banking Integration
- **EBICS Protocol Support**: Secure connection to bank accounts using EBICS 2.5/3.0
- **Multi-Bank Support**: Connect multiple bank accounts across different institutions
- **Transaction Synchronization**: Automated daily sync of bank statements (camt.053)
- **Real-time Balance Updates**: Monitor account balances and transaction history

### Intelligent Matching Engine
- **Automated Reconciliation**: AI-powered matching with confidence scoring
- **Multi-Criteria Matching**: Amount, IBAN, reference, and name-based matching
- **Confidence Thresholds**:
  - ≥90%: Auto-match
  - 50-89%: Suggestions
  - <50%: Manual review required
- **Manual Override**: User can manually match transactions when auto-matching fails

### Payment Processing
- **SEPA Payment Generation**: Create pain.001.001.03 XML files for SEPA transfers
- **Batch Payments**: Support for multiple payments in single SEPA file
- **Payment Validation**: ISO 20022 compliance and XML schema validation

### Advanced Features
- **Chargeback Detection**: Automatic identification of chargeback transactions
- **Duplicate Prevention**: Idempotent transaction processing
- **Audit Logging**: Complete audit trail for all operations
- **Error Handling**: Comprehensive error management with retry mechanisms
- **Security**: Encrypted credential storage and secure API access

### User Interface
- **Bank Accounts Dashboard**: Overview of connected accounts and sync status
- **Transaction Management**: List view with filtering and sorting
- **Matching Panel**: Interactive interface for manual matching
- **SEPA Payment Forms**: Easy payment creation from invoices

## Architecture & Implementation

### System Architecture

The app follows a clean architecture pattern with clear separation of concerns:

```
banking_integration/
├── api/              # Whitelisted API endpoints
├── doctype/          # DocType definitions and controllers
├── services/         # Business logic layer
│   ├── ebics_service.py     # EBICS communication
│   ├── matching_engine.py   # Transaction matching logic
│   ├── xml_generator.py     # SEPA XML generation
│   ├── parser.py           # camt.053 parsing
│   ├── sync.py            # Transaction synchronization
│   └── dunning.py         # Dunning process
├── utils/            # Utility functions
│   ├── encryption.py      # Password encryption
│   └── validation.py      # Data validation
└── page/             # UI pages
```

### Key Components

#### DocTypes
- **Bank Account**: Stores bank connection details and credentials
- **Bank Transaction**: Individual bank transactions with matching information

#### Services Layer
- **EBICS Service**: Handles secure communication with banks
- **Matching Engine**: Implements fuzzy matching algorithms
- **XML Services**: Generate and parse ISO 20022 XML formats

#### API Layer
- RESTful endpoints for external integrations
- Background job triggers
- Manual operation interfaces

### Matching Algorithm

The matching engine uses a weighted scoring system:

```python
weights = {
    'amount': 0.4,      # Exact amount match
    'iban': 0.3,        # IBAN verification
    'reference': 0.2,   # Reference similarity
    'name': 0.1         # Name similarity
}
```

Confidence scores determine matching actions:
- **90-100**: Automatic matching
- **50-89**: User suggestions
- **0-49**: Manual review required

### Security Implementation

- **Credential Encryption**: EBICS passwords encrypted using Fernet
- **API Security**: All endpoints whitelisted and role-based
- **Audit Logging**: All changes tracked with timestamps and user info
- **Data Protection**: Sensitive fields redacted in logs

## Installation

### Prerequisites

- ERPNext v14+ or v15+
- Frappe Framework v14+ or v15+
- Python 3.8+
- Valid EBICS credentials from your bank

### Install the App

1. **Get the app**:
   ```bash
   bench get-app banking_integration https://github.com/your-org/banking_integration.git
   ```

2. **Install on site**:
   ```bash
   bench --site your-site install-app banking_integration
   ```

3. **Migrate database**:
   ```bash
   bench --site your-site migrate
   ```

4. **Install dependencies**:
   ```bash
   bench --site your-site pip install -r apps/banking_integration/requirements.txt
   ```

### Post-Installation Setup

1. **Assign Roles**:
   - Assign "Accounts Manager" role to users who need access
   - System Manager has full access

2. **Configure Permissions**:
   - The app includes pre-configured permissions for Bank Account and Bank Transaction doctypes

## Configuration

### Bank Account Setup

1. **Create Bank Account**:
   - Go to Banking > Bank Accounts
   - Click "New Bank Account"
   - Fill in details:
     - Bank Account Name
     - Company
     - Bank Name
     - IBAN
     - EBICS User ID, Host ID, Partner ID
     - EBICS Password

2. **Test Connection**:
   - Use the "Test Connection" button
   - Verify EBICS credentials are valid

3. **Enable Account**:
   - Set "Is Active" to Yes
   - Status will show as "Active" after successful connection

### System Settings

The app uses standard ERPNext settings. Additional configuration can be done via:

- **Site Config**: Encryption keys are auto-generated
- **Scheduler**: Jobs run automatically (see Scheduler section)

## Usage

### Daily Operations

1. **Automatic Sync**:
   - Transactions sync daily at midnight via scheduler
   - Check Banking > Bank Accounts for sync status

2. **Review Matches**:
   - Go to Banking > Transactions
   - Review auto-matched transactions
   - Manually match unmatched transactions

3. **Generate Payments**:
   - From Purchase Invoice, use "Generate SEPA Payment"
   - Review and confirm payment details
   - Payment is sent to bank via EBICS

### Manual Operations

#### Sync Transactions Manually
```javascript
// From Bank Accounts page
frappe.call({
    method: 'banking_integration.api.bank_account.sync_transactions',
    args: { bank_account_name: 'ACCOUNT_NAME' }
});
```

#### Run Matching Engine
```javascript
frappe.call({
    method: 'banking_integration.api.transaction.run_matching_engine'
});
```

#### Manual Transaction Matching
```javascript
frappe.call({
    method: 'banking_integration.api.transaction.manual_match_transaction',
    args: {
        transaction_name: 'TXN_NAME',
        payment_name: 'PAYMENT_NAME'
    }
});
```

### API Reference

#### Bank Account APIs

- `connect_bank_account(bank_account_name)`: Test EBICS connection
- `sync_transactions(bank_account_name)`: Manual transaction sync

#### Transaction APIs

- `run_matching_engine()`: Execute matching for all unmatched transactions
- `manual_match_transaction(transaction_name, payment_name)`: Manual matching

#### Payment APIs

- `generate_sepa_payment(invoice_name)`: Create SEPA payment for invoice

### Scheduler Jobs

The app includes automated background jobs:

- **Daily (00:00)**: `sync_bank_transactions`
  - Syncs transactions for all active bank accounts
  - Updates last sync timestamps

- **Hourly**: `run_matching_engine`
  - Processes unmatched transactions
  - Updates confidence scores

- **Weekly**: `trigger_dunning`
  - Identifies overdue invoices
  - Triggers dunning process

Jobs can be monitored via ERPNext's Scheduler Logs.

## Security Considerations

### Credential Management
- EBICS passwords are encrypted at rest
- Encryption keys are site-specific and auto-generated
- No plain-text credentials in logs or database

### Access Control
- Role-based permissions (System Manager, Accounts Manager)
- API endpoints are whitelisted
- Audit logs track all user actions

### Data Protection
- IBAN and account numbers are redacted in user data exports
- Transaction amounts are logged but not sensitive data
- Secure communication via HTTPS/EBICS

## Troubleshooting

### Common Issues

#### EBICS Connection Failed
- Verify EBICS credentials with your bank
- Check network connectivity
- Review EBICS server certificates

#### Transactions Not Syncing
- Check scheduler is running: `bench doctor`
- Verify bank account is active
- Review error logs in Banking > Error Logs

#### Matching Not Working
- Ensure payments/invoices have reference numbers
- Check IBAN formats are correct
- Review matching confidence thresholds

#### SEPA Payment Errors
- Validate IBAN formats
- Check payment amounts
- Verify XML schema compliance

### Logs and Debugging

- **Error Logs**: Banking > Error Logs
- **Scheduler Logs**: ERPNext > Logs > Scheduled Job Logs
- **API Logs**: Check frappe.log for API calls

### Performance Tuning

For large transaction volumes:
- Increase scheduler frequency
- Optimize database indexes
- Consider batch processing for matching

## Development

### Running Tests
```bash
bench --site your-site run-tests banking_integration
```

### Code Structure
- Follow ERPNext/Frappe conventions
- Use type hints and docstrings
- Maintain separation between business logic and UI

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions:
- Documentation: [Link to docs]
- Issues: [GitHub Issues]
- Email: support@yourcompany.com

---

**Version**: 1.0.0
**Last Updated**: April 2026
**Compatible with**: ERPNext v14+, Frappe v14+
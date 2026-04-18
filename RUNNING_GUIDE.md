# Banking Integration App - Production Setup Guide

## Prerequisites
- Python 3.8+
- Node.js 14+
- Redis
- MariaDB/MySQL
- Git

## 1. Install Frappe Bench
```bash
pip install frappe-bench
```

## 2. Initialize Bench
```bash
bench init frappe-bench
cd frappe-bench
```

## 3. Create a New Site
```bash
bench new-site banking-demo.localhost
```

## 4. Install ERPNext
```bash
bench --site banking-demo.localhost install-app erpnext
```

## 5. Install Banking Integration App
```bash
# Copy the app to apps directory
cp -r /path/to/banking_integration apps/

# Install the app
bench --site banking-demo.localhost install-app banking_integration

# Migrate database
bench --site banking-demo.localhost migrate
```

## 6. Install Dependencies
```bash
bench --site banking-demo.localhost pip install lxml cryptography requests
```

## 7. Start Development Server
```bash
bench start
```

## 8. Access the Application
- Open browser: http://localhost:8000
- Login with Administrator credentials
- Go to Banking > Bank Accounts to set up your first bank account

## 9. Configure Bank Account
1. Create a new Bank Account record
2. Enter EBICS credentials (User ID, Host ID, Partner ID, Password)
3. Test connection using the "Test Connection" button
4. Enable the account by setting "Is Active" = Yes

## 10. Run Automated Jobs
```bash
# Manual sync
bench --site banking-demo.localhost execute banking_integration.services.sync.sync_bank_transactions

# Run matching engine
bench --site banking-demo.localhost execute banking_integration.services.matching.run_matching_engine
```

## 11. API Usage Examples

### Connect Bank Account
```javascript
frappe.call({
    method: 'banking_integration.api.bank_account.connect_bank_account',
    args: { bank_account_name: 'YOUR_BANK_ACCOUNT' },
    callback: function(r) {
        console.log(r.message);
    }
});
```

### Sync Transactions
```javascript
frappe.call({
    method: 'banking_integration.api.bank_account.sync_transactions',
    args: { bank_account_name: 'YOUR_BANK_ACCOUNT' },
    callback: function(r) {
        console.log(r.message);
    }
});
```

### Run Matching Engine
```javascript
frappe.call({
    method: 'banking_integration.api.transaction.run_matching_engine',
    callback: function(r) {
        console.log(r.message);
    }
});
```

### Generate SEPA Payment
```javascript
frappe.call({
    method: 'banking_integration.api.payment.generate_sepa_payment',
    args: { invoice_name: 'INV-001' },
    callback: function(r) {
        console.log('XML:', r.message.xml);
    }
});
```

## Troubleshooting

### Common Issues

1. **App not found**: Ensure the app is in the correct apps/ directory
2. **Dependencies missing**: Run `bench --site site-name pip install -r apps/banking_integration/requirements.txt`
3. **Permissions error**: Check user roles (Accounts Manager, System Manager)
4. **EBICS connection fails**: Verify credentials with your bank
5. **Scheduler not running**: Check bench doctor output

### Logs
```bash
# View site logs
bench --site banking-demo.localhost logs

# View scheduler logs
bench --site banking-demo.localhost doctor
```

## Production Deployment

For production deployment:

1. Set up proper SSL certificates
2. Configure firewall for EBICS ports
3. Set up backup procedures
4. Configure monitoring and alerts
5. Use production EBICS credentials
6. Set up proper user permissions

## Quick Test Commands

```bash
# Test app installation
bench --site banking-demo.localhost list-apps

# Test doctypes
bench --site banking-demo.localhost mariadb
USE banking-demo;
SHOW TABLES LIKE 'tabBank%';

# Test API
bench --site banking-demo.localhost console
frappe.get_all('Bank Account')
```
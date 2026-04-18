frappe.pages['bank-accounts'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Bank Accounts',
        single_column: true
    });

    // Add list view
    $(frappe.render_template('bank_accounts', {})).appendTo(page.main);

    // Load data
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Bank Account',
            fields: ['name', 'bank_name', 'iban', 'status', 'last_sync_date']
        },
        callback: function(r) {
            if (r.message) {
                // Render list
                var html = '<table class="table table-bordered">';
                html += '<thead><tr><th>Name</th><th>Bank</th><th>IBAN</th><th>Status</th><th>Last Sync</th><th>Actions</th></tr></thead><tbody>';
                r.message.forEach(function(account) {
                    html += `<tr>
                        <td>${account.name}</td>
                        <td>${account.bank_name}</td>
                        <td>${account.iban}</td>
                        <td>${account.status}</td>
                        <td>${account.last_sync_date || 'Never'}</td>
                        <td><button class="btn btn-sm btn-primary" onclick="syncAccount('${account.name}')">Sync</button></td>
                    </tr>`;
                });
                html += '</tbody></table>';
                $('.bank-accounts-list').html(html);
            }
        }
    });
}

function syncAccount(accountName) {
    frappe.call({
        method: 'banking_integration.api.bank_account.sync_transactions',
        args: { bank_account_name: accountName },
        callback: function(r) {
            if (r.message.status === 'success') {
                frappe.msgprint('Sync completed');
                location.reload();
            } else {
                frappe.msgprint('Sync failed: ' + r.message.message);
            }
        }
    });
}
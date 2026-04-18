frappe.pages['transactions'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Bank Transactions',
        single_column: true
    });

    // Add filters
    page.add_inner_button(__('Run Matching'), function() {
        frappe.call({
            method: 'banking_integration.api.transaction.run_matching_engine',
            callback: function(r) {
                frappe.msgprint(r.message.message);
            }
        });
    });

    // Load transactions
    load_transactions(page);
}

function load_transactions(page) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Bank Transaction',
            fields: ['name', 'transaction_date', 'amount', 'status', 'matched_payment', 'confidence_score', 'reference']
        },
        callback: function(r) {
            if (r.message) {
                var html = '<table class="table table-bordered">';
                html += '<thead><tr><th>Date</th><th>Amount</th><th>Reference</th><th>Status</th><th>Confidence</th><th>Actions</th></tr></thead><tbody>';
                r.message.forEach(function(tx) {
                    var actions = '';
                    if (tx.status === 'Unmatched') {
                        actions = `<button class="btn btn-sm btn-warning" onclick="showMatches('${tx.name}')">Match</button>`;
                    }
                    html += `<tr>
                        <td>${tx.transaction_date}</td>
                        <td>${tx.amount}</td>
                        <td>${tx.reference}</td>
                        <td>${tx.status}</td>
                        <td>${tx.confidence_score || ''}</td>
                        <td>${actions}</td>
                    </tr>`;
                });
                html += '</tbody></table>';
                page.main.html(html);
            }
        }
    });
}

function showMatches(txName) {
    // Show matching panel
    frappe.call({
        method: 'banking_integration.services.matching_engine.MatchingEngine.find_matches',
        args: { transaction: txName },
        callback: function(r) {
            // Show dialog with matches
            var dialog = new frappe.ui.Dialog({
                title: 'Potential Matches',
                fields: [
                    {
                        fieldtype: 'HTML',
                        options: '<div id="matches-list"></div>'
                    }
                ]
            });
            dialog.show();
            // Render matches
        }
    });
}
frappe.pages['payments'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Payments',
        single_column: true
    });

    // Render the payments template
    $(frappe.render_template('payments', {})).appendTo(page.main);

    // Load payments data
    load_payments();
}

function load_payments() {
    frappe.call({
        method: 'banking_integration.api.payments.get_payments',
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                var payments = r.message.payments;
                display_payments(payments);
                update_stats(payments);
            } else {
                $('#paymentsTable').html('<tr><td colspan="8" class="text-center text-danger">Error loading payments</td></tr>');
            }
        }
    });
}

function display_payments(payments) {
    if (payments.length === 0) {
        $('#paymentsTable').html('<tr><td colspan="8" class="text-center text-muted">No payments found</td></tr>');
        return;
    }

    var tbody = $('#paymentsTable');
    var html = payments.map(function(payment) {
        var amountClass = payment.amount > 0 ? 'amount-positive' : 'amount-negative';
        var statusClass = 'status-' + payment.status.toLowerCase();
        return `<tr>
            <td><span class="payment-id">${payment.payment_id}</span></td>
            <td><span class="${amountClass}">€${payment.amount.toFixed(2)}</span></td>
            <td>${payment.reference || 'N/A'}</td>
            <td><code class="iban-text">${payment.iban}</code></td>
            <td>${payment.bank_account}</td>
            <td><span class="${statusClass}">${payment.status}</span></td>
            <td>${new Date(payment.created_at).toLocaleDateString()}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="show_payment_details('${payment.payment_id}')">
                    <i class="fa fa-eye"></i> View
                </button>
            </td>
        </tr>`;
    }).join('');
    tbody.html(html);
}

function update_stats(payments) {
    var totalPayments = payments.length;
    var todayPayments = payments.filter(function(p) {
        var today = new Date().toDateString();
        return new Date(p.created_at).toDateString() === today;
    }).length;
    var completedPayments = payments.filter(function(p) { return p.status === 'Completed'; }).length;
    var totalAmount = payments.reduce(function(sum, p) { return sum + p.amount; }, 0);

    $('#totalPayments').text(totalPayments);
    $('#todayPayments').text(todayPayments);
    $('#completedPayments').text(completedPayments);
    $('#totalAmount').text('€' + totalAmount.toFixed(2));
}

function show_payment_details(paymentId) {
    frappe.call({
        method: 'banking_integration.api.payments.get_payment_details',
        args: { payment_id: paymentId },
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                var payment = r.message.payment;
                var detailsHtml = `
                    <div class="payment-details">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Payment ID:</strong> <span class="payment-id">${payment.payment_id}</span>
                            </div>
                            <div class="col-md-6">
                                <strong>Status:</strong> <span class="status-${payment.status.toLowerCase()}">${payment.status}</span>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Amount:</strong> <span class="amount-${payment.amount > 0 ? 'positive' : 'negative'} fw-bold">€${payment.amount.toFixed(2)}</span>
                            </div>
                            <div class="col-md-6">
                                <strong>Reference:</strong> ${payment.reference || 'N/A'}
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>IBAN:</strong> <code class="iban-text">${payment.iban}</code>
                            </div>
                            <div class="col-md-6">
                                <strong>Bank Account:</strong> ${payment.bank_account}
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Created Date:</strong> ${new Date(payment.created_at).toLocaleString()}
                            </div>
                            <div class="col-md-6">
                                <strong>Transaction ID:</strong> ${payment.transaction_id || 'N/A'}
                            </div>
                        </div>
                    </div>
                `;

                // Show in a dialog
                var d = new frappe.ui.Dialog({
                    title: 'Payment Details',
                    fields: [
                        {
                            fieldtype: 'HTML',
                            options: detailsHtml
                        }
                    ]
                });
                d.show();
            } else {
                frappe.msgprint('Error loading payment details');
            }
        }
    });
}
}

function showPaymentDetails(paymentId) {
    frappe.call({
        method: 'banking_integration.api.payments.get_payment_details',
        args: { payment_id: paymentId },
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                var payment = r.message.payment;
                
                var dialog = new frappe.ui.Dialog({
                    title: Payment Details - ,
                    fields: [
                        {
                            fieldtype: 'HTML',
                            options: 
                                <div class="payment-details">
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Payment ID:</strong> 
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Status:</strong> <span class="badge bg-success"></span>
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Amount:</strong> <span class="text-success fw-bold">€</span>
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Reference:</strong> 
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>IBAN:</strong> <code></code>
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Bank Account:</strong> 
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Created Date:</strong> 
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Transaction ID:</strong> 
                                        </div>
                                    </div>
                                </div>
                            
                        }
                    ],
                    size: 'large'
                });
                
                dialog.show();
            } else {
                frappe.msgprint('Error loading payment details');
            }
        }
    });
}

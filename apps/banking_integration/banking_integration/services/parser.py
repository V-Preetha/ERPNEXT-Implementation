import frappe
from lxml import etree
from datetime import datetime

def parse_camt053(xml_content):
    """Parse camt.053 XML and return list of transactions."""
    root = etree.fromstring(xml_content.encode('utf-8'))
    ns = {'camt': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.02'}

    transactions = []
    for entry in root.xpath('//camt:Ntry', namespaces=ns):
        amt_elem = entry.xpath('camt:Amt', namespaces=ns)[0]
        amount = float(amt_elem.text)
        currency = amt_elem.get('Ccy')

        cdt_dbt = entry.xpath('camt:CdtDbtInd', namespaces=ns)[0].text
        if cdt_dbt == 'DBIT':
            amount = -amount

        bookg_dt = entry.xpath('camt:BookgDt/camt:Dt', namespaces=ns)[0].text
        val_dt = entry.xpath('camt:ValDt/camt:Dt', namespaces=ns)[0].text

        tx_dtls = entry.xpath('camt:NtryDtls/camt:TxDtls', namespaces=ns)
        reference = ''
        iban = ''
        name = ''
        if tx_dtls:
            refs = tx_dtls[0].xpath('camt:Refs/camt:EndToEndId', namespaces=ns)
            if refs:
                reference = refs[0].text
            rltd_pties = tx_dtls[0].xpath('camt:RltdPties/camt:Dbtr', namespaces=ns)
            if rltd_pties:
                name_elem = rltd_pties[0].xpath('camt:Nm', namespaces=ns)
                if name_elem:
                    name = name_elem[0].text

        transaction = {
            'transaction_id': f"{bookg_dt}_{amount}_{reference}",
            'transaction_date': datetime.strptime(bookg_dt, '%Y-%m-%d').date(),
            'value_date': datetime.strptime(val_dt, '%Y-%m-%d').date(),
            'amount': amount,
            'currency': currency,
            'description': '',
            'reference': reference,
            'iban': iban,
            'name': name
        }
        transactions.append(transaction)

    return transactions
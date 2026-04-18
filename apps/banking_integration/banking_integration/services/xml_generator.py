from lxml import etree
from datetime import datetime

def generate_pain001(payment_data):
    """Generate pain.001.001.03 XML for SEPA payment."""
    ns = 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03'

    root = etree.Element('Document', nsmap={None: ns})
    cstmr_cdt_trf_initn = etree.SubElement(root, 'CstmrCdtTrfInitn')

    grp_hdr = etree.SubElement(cstmr_cdt_trf_initn, 'GrpHdr')
    msg_id = etree.SubElement(grp_hdr, 'MsgId')
    msg_id.text = payment_data.get('message_id', 'MSG001')
    cre_dt_tm = etree.SubElement(grp_hdr, 'CreDtTm')
    cre_dt_tm.text = datetime.now().isoformat()
    nb_of_txs = etree.SubElement(grp_hdr, 'NbOfTxs')
    nb_of_txs.text = '1'
    ctrl_sum = etree.SubElement(grp_hdr, 'CtrlSum')
    ctrl_sum.text = str(payment_data['amount'])
    initg_pty = etree.SubElement(grp_hdr, 'InitgPty')
    nm = etree.SubElement(initg_pty, 'Nm')
    nm.text = payment_data.get('initiator_name', 'Company Name')

    pmt_inf = etree.SubElement(cstmr_cdt_trf_initn, 'PmtInf')
    pmt_inf_id = etree.SubElement(pmt_inf, 'PmtInfId')
    pmt_inf_id.text = payment_data.get('payment_info_id', 'PMT001')
    pmt_mtd = etree.SubElement(pmt_inf, 'PmtMtd')
    pmt_mtd.text = 'TRF'
    nb_of_txs_pmt = etree.SubElement(pmt_inf, 'NbOfTxs')
    nb_of_txs_pmt.text = '1'
    ctrl_sum_pmt = etree.SubElement(pmt_inf, 'CtrlSum')
    ctrl_sum_pmt.text = str(payment_data['amount'])
    pmt_tp_inf = etree.SubElement(pmt_inf, 'PmtTpInf')
    svc_lvl = etree.SubElement(pmt_tp_inf, 'SvcLvl')
    cd = etree.SubElement(svc_lvl, 'Cd')
    cd.text = 'SEPA'
    reqd_exctn_dt = etree.SubElement(pmt_inf, 'ReqdExctnDt')
    reqd_exctn_dt.text = payment_data.get('execution_date', datetime.now().date().isoformat())
    dbtr = etree.SubElement(pmt_inf, 'Dbtr')
    nm_dbtr = etree.SubElement(dbtr, 'Nm')
    nm_dbtr.text = payment_data.get('debtor_name', 'Debtor Name')
    dbtr_acct = etree.SubElement(pmt_inf, 'DbtrAcct')
    id_dbtr = etree.SubElement(dbtr_acct, 'Id')
    iban_dbtr = etree.SubElement(id_dbtr, 'IBAN')
    iban_dbtr.text = payment_data['debtor_iban']
    dbtr_agt = etree.SubElement(pmt_inf, 'DbtrAgt')
    fin_instn_id = etree.SubElement(dbtr_agt, 'FinInstnId')
    bic = etree.SubElement(fin_instn_id, 'BIC')
    bic.text = payment_data.get('debtor_bic', 'DEUTDEFF')

    cdt_trf_tx_inf = etree.SubElement(pmt_inf, 'CdtTrfTxInf')
    pmt_id = etree.SubElement(cdt_trf_tx_inf, 'PmtId')
    end_to_end_id = etree.SubElement(pmt_id, 'EndToEndId')
    end_to_end_id.text = payment_data.get('end_to_end_id', 'E2E001')
    amt = etree.SubElement(cdt_trf_tx_inf, 'Amt')
    instd_amt = etree.SubElement(amt, 'InstdAmt', Ccy='EUR')
    instd_amt.text = str(payment_data['amount'])
    cdtr_agt = etree.SubElement(cdt_trf_tx_inf, 'CdtrAgt')
    fin_instn_id_cdtr = etree.SubElement(cdtr_agt, 'FinInstnId')
    bic_cdtr = etree.SubElement(fin_instn_id_cdtr, 'BIC')
    bic_cdtr.text = payment_data.get('creditor_bic', 'DEUTDEFF')
    cdtr = etree.SubElement(cdt_trf_tx_inf, 'Cdtr')
    nm_cdtr = etree.SubElement(cdtr, 'Nm')
    nm_cdtr.text = payment_data['creditor_name']
    cdtr_acct = etree.SubElement(cdt_trf_tx_inf, 'CdtrAcct')
    id_cdtr = etree.SubElement(cdtr_acct, 'Id')
    iban_cdtr = etree.SubElement(id_cdtr, 'IBAN')
    iban_cdtr.text = payment_data['creditor_iban']
    rmt_inf = etree.SubElement(cdt_trf_tx_inf, 'RmtInf')
    ustrd = etree.SubElement(rmt_inf, 'Ustrd')
    ustrd.text = payment_data.get('remittance_info', 'Payment')

    return etree.tostring(root, encoding='unicode', pretty_print=True)
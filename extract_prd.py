import zipfile

with zipfile.ZipFile('ERPNext_Banking_Integration_PRD_v1.0.docx', 'r') as zip_ref:
    zip_ref.extractall('temp')
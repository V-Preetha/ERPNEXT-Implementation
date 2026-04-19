import re
import frappe

def validate_iban(iban):
    """Validate IBAN format and checksum (mod-97 ISO 13616)."""
    if not iban:
        return False
    
    iban = iban.upper().replace(" ", "").replace("-", "")
    
    # Basic format: 2 letters, 2 digits, 1-30 alphanumeric
    if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$', iban):
        return False
    
    # Country-specific length validation
    country_lengths = {
        'AD': 24, 'AE': 23, 'AL': 28, 'AT': 20, 'AZ': 28, 'BA': 20, 'BE': 16,
        'BG': 22, 'BH': 22, 'BR': 29, 'BY': 28, 'CH': 21, 'CR': 22, 'CY': 28,
        'CZ': 24, 'DE': 22, 'DK': 18, 'DO': 28, 'EE': 20, 'EG': 29, 'ES': 24,
        'FI': 18, 'FO': 18, 'FR': 27, 'GB': 22, 'GE': 22, 'GI': 23, 'GL': 18,
        'GR': 27, 'GT': 28, 'HR': 21, 'HU': 28, 'IE': 22, 'IL': 23, 'IS': 26,
        'IT': 27, 'JO': 30, 'KW': 30, 'KZ': 20, 'LB': 28, 'LC': 32, 'LI': 21,
        'LT': 20, 'LU': 20, 'LV': 21, 'MC': 27, 'MD': 24, 'ME': 22, 'MK': 19,
        'MR': 27, 'MT': 31, 'MU': 30, 'NL': 18, 'NO': 15, 'PK': 24, 'PL': 28,
        'PS': 29, 'PT': 25, 'QA': 29, 'RO': 24, 'RS': 22, 'SA': 24, 'SE': 24,
        'SI': 19, 'SK': 24, 'SM': 27, 'TN': 24, 'TR': 26, 'UA': 29, 'VA': 22,
        'VG': 24, 'XK': 20
    }
    
    country = iban[:2]
    expected_length = country_lengths.get(country)
    if expected_length and len(iban) != expected_length:
        return False
    
    # Mod-97 checksum validation (ISO 13616)
    rearranged = iban[4:] + iban[:4]
    numeric_iban = ''
    for char in rearranged:
        if char.isdigit():
            numeric_iban += char
        else:
            numeric_iban += str(ord(char) - ord('A') + 10)
    
    return int(numeric_iban) % 97 == 1

def get_bank_account_by_iban(iban):
    """Retrieve bank account by IBAN."""
    try:
        accounts = frappe.get_all("Bank Account",
            filters={"iban": iban},
            fields=["name", "bank_name", "status"],
            limit_page_length=1)
        return accounts[0] if accounts else None
    except Exception:
        return None

def is_account_active(iban):
    """Check if bank account for given IBAN is active."""
    account = get_bank_account_by_iban(iban)
    return account and account.get("status") == "Active" if account else False

def validate_ebics_credentials(user_id, host_id, partner_id):
    """Validate EBICS credentials format."""
    if not all([user_id, host_id, partner_id]):
        return False
    # Add specific validations
    return True

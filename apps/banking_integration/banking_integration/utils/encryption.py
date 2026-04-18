import frappe
from cryptography.fernet import Fernet

def get_encryption_key():
    """Get or create encryption key for sensitive data."""
    key = frappe.get_site_config().get('encryption_key')
    if not key:
        key = Fernet.generate_key().decode()
        frappe.get_site_config()['encryption_key'] = key
        frappe.conf.update(frappe.get_site_config())
    return key.encode()

def encrypt_password(password):
    """Encrypt password using Fernet."""
    if not password:
        return password
    f = Fernet(get_encryption_key())
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    """Decrypt password."""
    if not encrypted_password:
        return encrypted_password
    f = Fernet(get_encryption_key())
    return f.decrypt(encrypted_password.encode()).decode()
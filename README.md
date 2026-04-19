# 🏦 ERPNext Banking Integration

An intelligent banking integration system for ERPNext that automates transaction reconciliation and enables SEPA payment generation.

---

## 🚀 What it does

- Connects bank transactions to ERP invoices  
- Automatically matches transactions using a confidence-based scoring system  
- Provides explainable matching (why something matched)  
- Generates SEPA payment files (ISO 20022 pain.001.001.03 XML)
- Handles edge cases like invalid IBAN and inactive accounts  

---

## 🧠 How it works

1. Import transactions  
2. Compare with invoices  
3. Calculate confidence score  
4. Classify:

- ✅ Matched (≥90%)
- ⚠️ Review (50–89%)
- 🟡 Unmatched (<50%)

5. Generate SEPA payments for invoices  

---


## 📸 Demo

### 💸 Transactions & Matching
<img width="1342" height="536" alt="image" src="https://github.com/user-attachments/assets/2f6f4901-d85f-4424-8439-8f9e9c0213a2" />



### 🔍 Explainable Matching
<img width="1331" height="775" alt="image" src="https://github.com/user-attachments/assets/5a2a51a1-ef56-4cf5-9e39-54bed758c003" />


### ⚠️ Validation (Invalid / Inactive)
<img width="1318" height="786" alt="image" src="https://github.com/user-attachments/assets/4d0e480c-881f-4165-bbbf-43b84a13116f" />


### 💳 SEPA Payment Generation
<img width="811" height="903" alt="image" src="https://github.com/user-attachments/assets/bbaa036b-05ca-4748-88e1-51f04c3286b3" />

---

## 🎯 Key Features

### 🧠 Explainable Matching Engine
Each transaction includes:
- Amount match  
- IBAN match  
- Reference match  
- Final confidence score  

### 💳 SEPA Payment Generation
- Generates ISO 20022 compliant **pain.001.001.03 XML**
- Supports structured bank transfer instructions
- Includes debtor/creditor validation
- Ready for EBICS bank submission (extensible)

---

## 🛠 Tech Stack

- Python (Frappe Framework)
- Flask (Demo UI)
- XML (camt.053 / pain.001)
- ERPNext Integration  

---

## ⚙️ Run Demo

```bash
pip install flask lxml cryptography
python ui_demo.py

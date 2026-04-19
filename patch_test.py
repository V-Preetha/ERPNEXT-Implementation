from pathlib import Path
p = Path("templates/transactions.html")
print("exists", p.exists())
text = p.read_text(encoding='utf-8')
print("len", len(text))

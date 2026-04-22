#!/usr/bin/env python
"""Extract and analyze PRD document."""
from zipfile import ZipFile
from lxml import etree
import os

# Path to the DOCX file (in parent directory)
docx_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ERPNext_Banking_Integration_PRD_v1.0.docx")

# Check if file exists
if os.path.exists(docx_path):
    print("Document found. Extracting content...")
    
    try:
        # Extract document.xml from DOCX (which is a ZIP file)
        with ZipFile(docx_path, 'r') as zip_ref:
            # Read the main document XML
            xml_content = zip_ref.read('word/document.xml')
            
        # Parse XML
        root = etree.fromstring(xml_content)
        
        # Define namespace
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        # Extract all text
        paragraphs = root.xpath('.//w:p', namespaces=ns)
        
        print(f"\nFound {len(paragraphs)} paragraphs\n")
        print("=" * 70)
        print("PRD DOCUMENT CONTENT:")
        print("=" * 70 + "\n")
        
        for para in paragraphs:
            # Extract text from all runs in the paragraph
            texts = para.xpath('.//w:t/text()', namespaces=ns)
            if texts:
                line = ''.join(texts)
                print(line)
            
    except Exception as e:
        print(f"Error reading document: {e}")
else:
    print(f"Document not found at {docx_path}")
    print("Current directory:", os.getcwd())
    print("Available files:", os.listdir()[:10])

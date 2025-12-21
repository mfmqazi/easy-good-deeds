"""
Extract content from Fazail-e-Amaal PDF and create structured data for the website.
"""
import fitz  # PyMuPDF
import json
import re
import os

def extract_text_from_pdf(pdf_path):
    """Extract all text from PDF."""
    doc = fitz.open(pdf_path)
    full_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        full_text.append({
            "page": page_num + 1,
            "text": text
        })
    
    doc.close()
    return full_text

def identify_chapters(pages):
    """Identify chapters and sections from the extracted text."""
    chapters = []
    current_chapter = None
    current_section = None
    
    # Known main sections in Fazail-e-Amaal
    main_sections = [
        "Virtues of Salat",
        "Virtues of Prayer",
        "Fazail-e-Salat",
        "Virtues of Quran",
        "Fazail-e-Quran",
        "Virtues of Dhikr",
        "Virtues of Zikr", 
        "Fazail-e-Dhikr",
        "Virtues of Tabligh",
        "Fazail-e-Tabligh",
        "Virtues of Ramadan",
        "Fazail-e-Ramadan",
        "Virtues of Hajj",
        "Fazail-e-Hajj",
        "Virtues of Sadaqat",
        "Virtues of Charity",
        "Fazail-e-Sadaqat",
        "Stories of Sahabah",
        "Hikayat-e-Sahabah"
    ]
    
    for page_data in pages:
        text = page_data["text"]
        page_num = page_data["page"]
        
        # Check for chapter headers
        for section in main_sections:
            if section.lower() in text.lower():
                if current_chapter:
                    chapters.append(current_chapter)
                current_chapter = {
                    "title": section,
                    "start_page": page_num,
                    "content": text,
                    "sections": []
                }
                break
        
        if current_chapter:
            current_chapter["content"] += "\n" + text
    
    if current_chapter:
        chapters.append(current_chapter)
    
    return chapters

def create_structured_content(pdf_path):
    """Create structured content from PDF."""
    print(f"Extracting text from: {pdf_path}")
    pages = extract_text_from_pdf(pdf_path)
    
    print(f"Extracted {len(pages)} pages")
    
    # Save raw text for reference
    with open("fazail_full_text.txt", "w", encoding="utf-8") as f:
        for page in pages:
            f.write(f"\n--- Page {page['page']} ---\n")
            f.write(page["text"])
    
    print("Saved full text to fazail_full_text.txt")
    
    # Try to identify structure
    chapters = identify_chapters(pages)
    print(f"Identified {len(chapters)} potential chapters")
    
    # Create a summary of the first few pages to understand structure
    summary = []
    for i, page in enumerate(pages[:20]):  # First 20 pages
        summary.append({
            "page": page["page"],
            "preview": page["text"][:500] if len(page["text"]) > 500 else page["text"]
        })
    
    with open("fazail_structure_preview.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("Saved structure preview to fazail_structure_preview.json")
    
    return pages, chapters

if __name__ == "__main__":
    pdf_path = "fazail-e-amal-virtues-of-deeds.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
    else:
        pages, chapters = create_structured_content(pdf_path)
        
        # Print first few pages content for analysis
        print("\n" + "="*50)
        print("FIRST 10 PAGES PREVIEW:")
        print("="*50)
        for page in pages[:10]:
            print(f"\n--- PAGE {page['page']} ---")
            print(page["text"][:800])

import json
import re
import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return None

    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text

def parse_deeds(text):
    # This regex assumes deeds start with a number and a title, similar to the data.js structure
    # Adjust regex based on actual PDF content format
    # Example pattern: "1. Good Intention" or "Deed 1: Good Intention"
    # For now, I'll use a pattern that looks for the titles present in data.js
    
    # Load existing data to get titles/IDs
    with open('data.js', 'r', encoding='utf-8') as f:
        content = f.read()
        # Extract the array part roughly
        json_str = content[content.find('['):content.rfind(']')+1]
        # This is JS object syntax, not valid JSON (keys not quoted), so we can't just json.loads it easily
        # We'll rely on the text extraction and some heuristics for now.
    
    # Let's try to split by "Deed #" or just look for the titles.
    # Since I don't have the PDF content yet, I'll write a generic splitter that looks for
    # numeric headers which likely indicate new deeds.
    
    deeds = []
    # Placeholder logic: Split by something that looks like a header
    # In the other project, they split by pages. Here deeds might be short.
    
    # Heuristic: Look for lines starting with a number followed by a dot or close paren
    # e.g. "1. " or "1) "
    
    lines = text.split('\n')
    current_deed = {"id": None, "title": "", "content": ""}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for start of a new deed
        # Regex: Start of line, 1-3 digits, dot, space, text
        match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if match:
            # Save previous deed if it exists
            if current_deed["id"] is not None:
                deeds.append(current_deed)
            
            current_deed = {
                "id": int(match.group(1)),
                "title": match.group(2),
                "content": ""
            }
        else:
            if current_deed["id"] is not None:
                current_deed["content"] += line + " "
                
    # Append last deed
    if current_deed["id"] is not None:
        deeds.append(current_deed)
        
    return deeds

def main():
    pdf_path = "easy-good-deeds.pdf"
    print(f"Extracting text from {pdf_path}...")
    
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return

    print("Parsing deeds...")
    deeds = parse_deeds(text)
    
    print(f"Found {len(deeds)} deeds.")
    
    # Save to JSON
    with open("deeds_content.json", "w", encoding="utf-8") as f:
        json.dump(deeds, f, indent=4)
    print("Saved to deeds_content.json")

if __name__ == "__main__":
    main()

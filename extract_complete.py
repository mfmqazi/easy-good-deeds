"""
Comprehensive extraction of Fazail-e-Amaal PDF
Extracts all stories, chapters, and Arabic text with proper structure
"""
import fitz  # PyMuPDF
import json
import re
import os

# Book definitions with their page ranges (approximate)
BOOKS = {
    1: {"title": "Stories of Sahaabah", "arabic": "حکایاتِ صحابہ", "start_page": 3, "end_page": 130},
    2: {"title": "Virtues of Holy Qur'aan", "arabic": "فضائلِ قرآن", "start_page": 131, "end_page": 180},
    3: {"title": "Virtues of Salaat", "arabic": "فضائلِ نماز", "start_page": 181, "end_page": 260},
    4: {"title": "Virtues of Zikr", "arabic": "فضائلِ ذکر", "start_page": 261, "end_page": 320},
    5: {"title": "Virtues of Tabligh", "arabic": "فضائلِ تبلیغ", "start_page": 321, "end_page": 370},
    6: {"title": "Virtues of Ramadhaan", "arabic": "فضائلِ رمضان", "start_page": 371, "end_page": 420},
    7: {"title": "Muslim Degeneration", "arabic": "مسلمانوں کی پستی", "start_page": 421, "end_page": 440},
    8: {"title": "Six Fundamentals", "arabic": "چھ اصول", "start_page": 441, "end_page": 452},
}

def is_arabic_text(text):
    """Check if text contains Arabic characters."""
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    return bool(arabic_pattern.search(text))

def extract_with_arabic_detection(pdf_path):
    """Extract text with Arabic detection and positioning."""
    doc = fitz.open(pdf_path)
    all_content = []
    
    print(f"Processing {len(doc)} pages...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get text blocks with position info
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        
        page_content = {
            "page": page_num + 1,
            "segments": []
        }
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            is_arabic = is_arabic_text(text)
                            page_content["segments"].append({
                                "text": text,
                                "is_arabic": is_arabic,
                                "font": span.get("font", ""),
                                "size": span.get("size", 0),
                                "y_position": span.get("origin", [0, 0])[1] if "origin" in span else 0
                            })
        
        all_content.append(page_content)
        
        if (page_num + 1) % 50 == 0:
            print(f"  Processed {page_num + 1} pages...")
    
    doc.close()
    return all_content

def identify_chapters_and_stories(content):
    """Identify chapter headers and story titles from the extracted content."""
    chapters = []
    stories = []
    
    current_book = 1
    current_chapter = None
    current_story = None
    story_id = 0
    
    # Chapter patterns for Stories of Sahaabah
    chapter_patterns = [
        (r"CHAPTER\s+([IVX]+|[0-9]+)", "chapter"),
        (r"Ch\.\s*([IVX]+|[0-9]+):", "chapter_ref"),
    ]
    
    # Story title patterns (numbered items)
    story_pattern = re.compile(r'^(\d+)\.\s+(.+?)(?:\s*\(|:|\n|$)')
    
    for page_data in content:
        page_num = page_data["page"]
        
        # Determine which book this page belongs to
        for book_id, book_info in BOOKS.items():
            if book_info["start_page"] <= page_num <= book_info["end_page"]:
                current_book = book_id
                break
        
        # Combine segments into full text for pattern matching
        page_text = ""
        for seg in page_data["segments"]:
            page_text += seg["text"] + " "
        
        # Check for chapter headers
        for pattern, ptype in chapter_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                chapter_num = match.group(1)
                # Try to extract chapter title
                title_match = re.search(pattern + r'\s*[:\n]?\s*(.+?)(?:\.|$)', page_text, re.IGNORECASE)
                if title_match and len(title_match.groups()) > 1:
                    title = title_match.group(2)[:100]  # Limit title length
                else:
                    title = f"Chapter {chapter_num}"
                
                current_chapter = {
                    "id": len(chapters) + 1,
                    "book_id": current_book,
                    "number": chapter_num,
                    "title": title.strip(),
                    "start_page": page_num
                }
                chapters.append(current_chapter)
        
        # Check for story titles (numbered entries like "1. Prophet's Journey to Taif")
        story_matches = story_pattern.findall(page_text)
        for num, title in story_matches:
            title = title.strip()
            if len(title) > 10 and len(title) < 150:
                story_id += 1
                stories.append({
                    "id": story_id,
                    "book_id": current_book,
                    "chapter_id": current_chapter["id"] if current_chapter else None,
                    "number": int(num),
                    "title": title,
                    "start_page": page_num
                })
    
    return chapters, stories

def extract_story_content(content, story, next_story=None):
    """Extract the full content of a story including inline Arabic text."""
    start_page = story["start_page"]
    end_page = next_story["start_page"] if next_story else start_page + 5
    
    story_content = []
    in_story = False
    
    for page_data in content:
        page_num = page_data["page"]
        
        if page_num < start_page:
            continue
        if page_num > end_page:
            break
        
        for seg in page_data["segments"]:
            text = seg["text"]
            
            # Check if we're at the story title
            if story["title"][:30] in text:
                in_story = True
            
            if in_story:
                if seg["is_arabic"]:
                    # Format Arabic text with special marker
                    story_content.append({
                        "type": "arabic",
                        "text": text
                    })
                else:
                    story_content.append({
                        "type": "english",
                        "text": text
                    })
    
    return story_content

def process_full_pdf():
    """Main function to process the entire PDF."""
    pdf_path = "fazail-e-amal-virtues-of-deeds.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        return
    
    print("=" * 60)
    print("FAZAIL-E-AMAAL COMPLETE PDF EXTRACTION")
    print("=" * 60)
    
    # Step 1: Extract all content with Arabic detection
    print("\n[1/4] Extracting text with Arabic detection...")
    content = extract_with_arabic_detection(pdf_path)
    print(f"  Extracted {len(content)} pages")
    
    # Step 2: Identify chapters and stories
    print("\n[2/4] Identifying chapters and stories...")
    chapters, stories = identify_chapters_and_stories(content)
    print(f"  Found {len(chapters)} chapters and {len(stories)} stories")
    
    # Step 3: Save structured data
    print("\n[3/4] Creating structured data...")
    
    # Save page-by-page content with Arabic segments
    pages_with_arabic = []
    arabic_segment_count = 0
    
    for page_data in content:
        arabic_segments = [s for s in page_data["segments"] if s["is_arabic"]]
        if arabic_segments:
            pages_with_arabic.append({
                "page": page_data["page"],
                "arabic_count": len(arabic_segments),
                "arabic_texts": [s["text"] for s in arabic_segments]
            })
            arabic_segment_count += len(arabic_segments)
    
    print(f"  Found {arabic_segment_count} Arabic text segments across {len(pages_with_arabic)} pages")
    
    # Step 4: Create the final structured output
    print("\n[4/4] Generating output files...")
    
    # Save extracted data
    output = {
        "books": [
            {
                "id": book_id,
                "title": info["title"],
                "arabic": info["arabic"],
                "start_page": info["start_page"],
                "end_page": info["end_page"],
                "story_count": len([s for s in stories if s["book_id"] == book_id])
            }
            for book_id, info in BOOKS.items()
        ],
        "chapters": chapters,
        "stories": stories,
        "pages_with_arabic": pages_with_arabic[:50],  # Sample of pages with Arabic
        "stats": {
            "total_pages": len(content),
            "total_chapters": len(chapters),
            "total_stories": len(stories),
            "arabic_segments": arabic_segment_count
        }
    }
    
    with open("fazail_extracted.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n  Saved to fazail_extracted.json")
    
    # Also save the full page content for reference
    full_content = []
    for page_data in content:
        page_text = ""
        for seg in page_data["segments"]:
            if seg["is_arabic"]:
                page_text += f'\n<arabic>{seg["text"]}</arabic>\n'
            else:
                page_text += seg["text"] + " "
        
        full_content.append({
            "page": page_data["page"],
            "content": page_text.strip()
        })
    
    with open("fazail_full_content.json", "w", encoding="utf-8") as f:
        json.dump(full_content, f, indent=2, ensure_ascii=False)
    
    print("  Saved full content to fazail_full_content.json")
    
    # Print summary
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"\nTotal Pages: {len(content)}")
    print(f"Total Chapters: {len(chapters)}")
    print(f"Total Stories: {len(stories)}")
    print(f"Arabic Segments: {arabic_segment_count}")
    print("\nBooks breakdown:")
    for book_id, info in BOOKS.items():
        story_count = len([s for s in stories if s["book_id"] == book_id])
        print(f"  {book_id}. {info['title']}: {story_count} stories")

if __name__ == "__main__":
    process_full_pdf()

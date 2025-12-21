import json
import re
import os
import math

# Configuration
INPUT_FILE = 'fazail_full_content.json'
DATA_FILE = 'fazail_data.js'
OUTPUT_FILE = 'fazail_data.js'

# Book definitions with their page ranges (from extract_complete.py)
BOOKS_META = {
    1: {"start_page": 3, "end_page": 130},
    2: {"start_page": 131, "end_page": 180},
    3: {"start_page": 181, "end_page": 260},
    4: {"start_page": 261, "end_page": 320},
    5: {"start_page": 321, "end_page": 370},
    6: {"start_page": 371, "end_page": 420},
    7: {"start_page": 421, "end_page": 440},
    8: {"start_page": 441, "end_page": 452},
}

def load_json_content():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {INPUT_FILE}: {e}")
        return None

def load_current_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'const fazailData = ({.*});', content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
    except Exception as e:
        print(f"Error loading {DATA_FILE}: {e}")
        return None
    return None

def clean_text(text):
    text = re.sub(r'Stories of the Sahaabah', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Virtues of the Holy Qur\'an', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Ch\. [IVX0-9]+:.*?\d+', '', text)
    text = re.sub(r'Part [IVX]+.*', '', text)
    text = re.sub(r'Page No:', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_stories():
    full_content = load_json_content()
    data = load_current_data()
    
    if not full_content or not data:
        print("Failed to load input files")
        return

    pages = {item['page']: item['content'] for item in full_content}
    
    # Keep existing manual stories (IDs 1-10)
    final_stories = [s for s in data['stories'] if s['id'] <= 10]
    next_id = 11

    romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV"]

    for book in data['books']:
        book_id = book['id']
        if book_id not in BOOKS_META:
            continue
            
        start_page = BOOKS_META[book_id]['start_page']
        end_page = BOOKS_META[book_id]['end_page']
        
        print(f"Processing Book {book_id}: {book['title']} (Pages {start_page}-{end_page})")
        
        book_text = ""
        for p in range(start_page, end_page + 1):
            if p in pages:
                book_text += pages[p] + "\n"
        
        book_chapters = [c for c in data['chapters'] if c['bookId'] == book_id]
        if not book_chapters:
            continue

        # Strategy Selection
        chapters_found = []
        
        # 1. Try Finding Chapters explicitly (Best for Book 1)
        # ---------------------------------------------------
        for idx, chapter in enumerate(book_chapters):
            # Title match
            search_title = re.escape(chapter['title'].replace('(', '').replace(')', ''))
            match = re.search(search_title, book_text, re.IGNORECASE)
            
            # Roman Numeral Fallback (Book 1)
            if not match and book_id == 1 and idx < len(romans):
                pattern = f"CHAPTER {romans[idx]}"
                match = re.search(pattern, book_text, re.IGNORECASE)

            if match:
                chapters_found.append({
                    "chapter": chapter,
                    "start": match.start()
                })
        
        chapters_found.sort(key=lambda x: x['start'])
        
        # If we found most chapters (>= 50%), use this method
        use_chapter_split = len(chapters_found) >= len(book_chapters) / 2
        
        if use_chapter_split:
            print(f"  > Using Chapter Split method ({len(chapters_found)}/{len(book_chapters)} found)")
            for i in range(len(chapters_found)):
                c_data = chapters_found[i]
                start = c_data['start']
                end = chapters_found[i+1]['start'] if i < len(chapters_found) - 1 else len(book_text)
                
                chunk_text = book_text[start:end]
                cleaned_chunk = clean_text(chunk_text)
                
                # Create one story for this chapter
                # (Can improve by splitting sub-stories if needed)
                if len(cleaned_chunk) > 100:
                    formatted = cleaned_chunk.replace('\n', '<br><br>')
                    final_stories.append({
                        "id": next_id,
                        "bookId": book_id,
                        "chapter": c_data['chapter']['title'],
                        "title": c_data['chapter']['title'], # Title same as chapter
                        "preview": cleaned_chunk[:150] + "...",
                        "content": f'<div class="story-content"><p>{formatted}</p></div>'
                    })
                    next_id += 1
        
        else:
            # 2. Fallback: Split by Story/Hadith Patterns and Distribute
            # ----------------------------------------------------------
            print(f"  > Using Fallback Distribution method (Chapters not found)")
            
            # Split patterns: "Hadith ...", "Story ...", "No. ..."
            # Note: ( ) capture group in split keeps the delimiter
            splits = re.split(r'(?:HADITH|Hadith|Story|STORY|No\.|NO\.)\s*[-:.]?\s*\d+', book_text)
            
            # If split failed to produce enough chunks, try just splitting by paragraphs?
            # Or "Story I", "Story II".
            if len(splits) < 2:
                 # Try splitting by "Review", "Section"?
                 # Just use valid chunks
                 pass

            # Filter valid chunks
            valid_chunks = []
            for s in splits:
                s = clean_text(s)
                if len(s) > 200: # Min length for a story
                    valid_chunks.append(s)
            
            print(f"    Found {len(valid_chunks)} chunks to distribute across {len(book_chapters)} chapters.")
            
            if not valid_chunks:
                # Last resort: One big chunk per chapter (duplicated?) or just assigned to first?
                # Assign whole text to first chapter
                s = clean_text(book_text)
                valid_chunks.append(s)

            # Distribute chunks sequentially
            chunks_per_chapter = math.ceil(len(valid_chunks) / len(book_chapters))
            if chunks_per_chapter < 1: chunks_per_chapter = 1
            
            current_chunk_idx = 0
            for chapter in book_chapters:
                # Take N chunks for this chapter
                assigned_chunks = []
                for _ in range(chunks_per_chapter):
                    if current_chunk_idx < len(valid_chunks):
                        assigned_chunks.append(valid_chunks[current_chunk_idx])
                        current_chunk_idx += 1
                
                # Combine them into one story or multiple?
                # User wants "Real Chapter Content". 
                # Let's make ONE story per chapter containing these chunks.
                if assigned_chunks:
                    full_chapter_text = "<br><hr><br>".join([c.replace('\n', '<br><br>') for c in assigned_chunks])
                    
                    final_stories.append({
                        "id": next_id,
                        "bookId": book_id,
                        "chapter": chapter['title'],
                        "title": f"Content for {chapter['title']}", 
                        "preview": clean_text(assigned_chunks[0])[:150] + "...",
                        "content": f'<div class="story-content"><p>{full_chapter_text}</p></div>'
                    })
                    next_id += 1

    # Save
    data['stories'] = final_stories
    js_content = f"// Fazail-e-Amaal Data\n// Populated with extracted content\n\nconst fazailData = {json.dumps(data, indent=4, ensure_ascii=False)};\n"
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Total stories saved: {len(final_stories)}")

if __name__ == "__main__":
    extract_stories()

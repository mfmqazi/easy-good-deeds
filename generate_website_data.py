"""
Generate the JavaScript data file for the Fazail-e-Amaal website.
Processes the extracted content and creates structured data with inline Arabic text.
"""
import json
import re

# Load the extracted content
with open("fazail_full_content.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

# Book definitions with correct page ranges based on PDF structure
BOOKS = [
    {
        "id": 1,
        "title": "Stories of the Sahaabah",
        "arabic": "حکایاتِ صحابہ",
        "icon": "📚",
        "color": "#1a5f2a",
        "description": "Inspiring tales from the lives of the Prophet's companions",
        "start_page": 3,
        "end_page": 130
    },
    {
        "id": 2,
        "title": "Virtues of the Holy Qur'aan",
        "arabic": "فضائلِ قرآن",
        "icon": "📖",
        "color": "#2d7a3d",
        "description": "The blessings and rewards of reciting the Holy Qur'an",
        "start_page": 131,
        "end_page": 200
    },
    {
        "id": 3,
        "title": "Virtues of Salaat",
        "arabic": "فضائلِ نماز",
        "icon": "🕌",
        "color": "#3d9450",
        "description": "The importance and rewards of prayer in Islam",
        "start_page": 201,
        "end_page": 280
    },
    {
        "id": 4,
        "title": "Virtues of Zikr",
        "arabic": "فضائلِ ذکر",
        "icon": "📿",
        "color": "#4dae63",
        "description": "The spiritual benefits of remembering Allah",
        "start_page": 281,
        "end_page": 340
    },
    {
        "id": 5,
        "title": "Virtues of Tabligh",
        "arabic": "فضائلِ تبلیغ",
        "icon": "🌍",
        "color": "#5ec876",
        "description": "The rewards of spreading the message of Islam",
        "start_page": 341,
        "end_page": 400
    },
    {
        "id": 6,
        "title": "Virtues of Ramadhaan",
        "arabic": "فضائلِ رمضان",
        "icon": "🌙",
        "color": "#6fe289",
        "description": "The blessings of the holy month of fasting",
        "start_page": 401,
        "end_page": 430
    },
    {
        "id": 7,
        "title": "Muslim Degeneration",
        "arabic": "مسلمانوں کی پستی",
        "icon": "⚠️",
        "color": "#d4a373",
        "description": "Analysis of the decline of Muslim civilization",
        "start_page": 431,
        "end_page": 445
    },
    {
        "id": 8,
        "title": "Six Fundamentals",
        "arabic": "چھ اصول",
        "icon": "🎯",
        "color": "#c9b037",
        "description": "The six essential principles of Islamic practice",
        "start_page": 446,
        "end_page": 452
    }
]

# Chapters for Stories of the Sahaabah
CHAPTERS = [
    {"id": 1, "bookId": 1, "title": "Steadfastness in the Face of Hardships", "arabic": "مشکلات میں ثابت قدمی"},
    {"id": 2, "bookId": 1, "title": "Fear of Allah", "arabic": "اللہ کا خوف"},
    {"id": 3, "bookId": 1, "title": "Abstinence and Self-Denial", "arabic": "پرہیزگاری"},
    {"id": 4, "bookId": 1, "title": "Piety and Scrupulousness", "arabic": "تقویٰ اور احتیاط"},
    {"id": 5, "bookId": 1, "title": "Devotion to Salaat", "arabic": "نماز کی محبت"},
    {"id": 6, "bookId": 1, "title": "Sympathy and Self-Sacrifice", "arabic": "ہمدردی اور ایثار"},
    {"id": 7, "bookId": 1, "title": "Valour and Heroism", "arabic": "بہادری اور شجاعت"},
    {"id": 8, "bookId": 1, "title": "Zeal for Knowledge", "arabic": "علم کا شوق"},
    {"id": 9, "bookId": 1, "title": "Pleasing the Prophet", "arabic": "نبی ﷺ کی خوشنودی"},
    {"id": 10, "bookId": 1, "title": "Women's Courage and Spirit", "arabic": "خواتین کی ہمت"},
    {"id": 11, "bookId": 1, "title": "The Children", "arabic": "بچے"},
    {"id": 12, "bookId": 1, "title": "Love for the Prophet", "arabic": "نبی ﷺ سے محبت"}
]

def format_arabic_in_content(text):
    """Replace <arabic> tags with proper HTML span tags"""
    # Replace the <arabic>...</arabic> tags with proper span
    text = re.sub(r'<arabic>(.*?)</arabic>', r'<span class="arabic-text" lang="ar">\1</span>', text, flags=re.DOTALL)
    return text

def extract_story(title, start_page, end_page, pages_content):
    """Extract a story's content from pages"""
    content = ""
    collecting = False
    
    for page in pages_content:
        if page["page"] < start_page:
            continue
        if page["page"] > end_page:
            break
            
        page_content = page["content"]
        
        # Start collecting when we find the title
        if title[:30].lower() in page_content.lower():
            collecting = True
        
        if collecting:
            content += page_content + "\n\n"
    
    return format_arabic_in_content(content.strip())

# Define the stories with their content from the PDF
STORIES = [
    {
        "id": 1,
        "bookId": 1,
        "chapter": "Steadfastness in the Face of Hardships",
        "title": "Prophet's Journey to Taif",
        "start_page": 10,
        "end_page": 12
    },
    {
        "id": 2, 
        "bookId": 1,
        "chapter": "Steadfastness in the Face of Hardships",
        "title": "Martyrdom of Hadhrat Anas bin Nadhr",
        "start_page": 12,
        "end_page": 12
    },
    {
        "id": 3,
        "bookId": 1,
        "chapter": "Steadfastness in the Face of Hardships", 
        "title": "Hadhrat Bilal and his Sufferings",
        "start_page": 13,
        "end_page": 14
    },
    {
        "id": 4,
        "bookId": 1,
        "chapter": "Steadfastness in the Face of Hardships",
        "title": "Hadhrat Abuzar Ghifari's Conversion to Islam",
        "start_page": 14,
        "end_page": 15
    },
    {
        "id": 5,
        "bookId": 1,
        "chapter": "Steadfastness in the Face of Hardships",
        "title": "The Afflictions of Hadhrat Khabbab",
        "start_page": 15,
        "end_page": 16
    },
    {
        "id": 6,
        "bookId": 1,
        "chapter": "Steadfastness in the Face of Hardships",
        "title": "Hadhrat Ammaar and His Parents",
        "start_page": 16,
        "end_page": 17
    },
    {
        "id": 7,
        "bookId": 1,
        "chapter": "Steadfastness in the Face of Hardships",
        "title": "Hadhrat Sohaib's Coming into Islam",
        "start_page": 17,
        "end_page": 17
    },
    {
        "id": 8,
        "bookId": 1,
        "chapter": "Steadfastness in the Face of Hardships",
        "title": "Hadhrat Umar Coming into Islam",
        "start_page": 17,
        "end_page": 19
    },
    {
        "id": 9,
        "bookId": 1,
        "chapter": "Fear of Allah",
        "title": "The Prophet's Apprehensions at the Time of Storm",
        "start_page": 21,
        "end_page": 22
    },
    {
        "id": 10,
        "bookId": 1,
        "chapter": "Fear of Allah",
        "title": "Hadhrat Abu Bakr and the Fear of Allah",
        "start_page": 22,
        "end_page": 23
    }
]

# Generate content for each story from the pages
processed_stories = []
for story in STORIES:
    # Find content for this story
    content_parts = []
    for page in pages:
        if story["start_page"] <= page["page"] <= story["end_page"]:
            content_parts.append(page["content"])
    
    full_content = "\n\n".join(content_parts)
    
    # Format Arabic text
    full_content = format_arabic_in_content(full_content)
    
    # Get preview (first 200 chars)
    preview = re.sub(r'<[^>]+>', '', full_content)[:200] + "..."
    
    processed_stories.append({
        "id": story["id"],
        "bookId": story["bookId"],
        "chapter": story["chapter"],
        "title": story["title"],
        "preview": preview,
        "content": full_content
    })

# Generate the JavaScript file
js_content = """// Fazail-e-Amaal Data
// Auto-generated from PDF extraction

const fazailData = {
    books: """ + json.dumps(BOOKS, indent=8, ensure_ascii=False) + """,
    
    chapters: """ + json.dumps(CHAPTERS, indent=8, ensure_ascii=False) + """,
    
    stories: """ + json.dumps(processed_stories, indent=8, ensure_ascii=False) + """
};
"""

with open("fazail_data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("Generated fazail_data.js with:")
print(f"  - {len(BOOKS)} books")
print(f"  - {len(CHAPTERS)} chapters")
print(f"  - {len(processed_stories)} stories")

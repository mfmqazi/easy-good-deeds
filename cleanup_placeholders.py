import json
import re

DATA_FILE = 'fazail_data.js'

def cleanup():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'const fazailData = ({.*});', content, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            
            # Remove stories with ID 1-10 (Placeholders)
            original_count = len(data['stories'])
            data['stories'] = [s for s in data['stories'] if s['id'] > 10]
            new_count = len(data['stories'])
            
            print(f"Removed {original_count - new_count} placeholder stories (IDs 1-10).")
            
            js_content = f"// Fazail-e-Amaal Data\n// Cleaned real content\n\nconst fazailData = {json.dumps(data, indent=4, ensure_ascii=False)};\n"
            
            with open(DATA_FILE, 'w', encoding='utf-8') as f_out:
                f_out.write(js_content)

if __name__ == "__main__":
    cleanup()

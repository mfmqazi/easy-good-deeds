import re
import json

def parse_data_js(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the array content
    # Look for const deeds = [...];
    match = re.search(r'const deeds = \[(.*?)\];', content, re.DOTALL)
    if not match:
        print("Could not find deeds array")
        return []
    
    array_content = match.group(1)
    
    # Parse objects
    # This is a bit hacky because it's JS not JSON (keys aren't quoted)
    # We'll use regex to extract id, title, description
    
    deeds = []
    # Split by "}," to get individual objects roughly
    objects = array_content.split('},')
    
    for obj in objects:
        obj = obj.strip()
        if not obj:
            continue
            
        # Extract ID
        id_match = re.search(r'id:\s*(\d+)', obj)
        # Extract Title
        title_match = re.search(r'title:\s*"(.*?)"', obj)
        # Extract Description
        desc_match = re.search(r'description:\s*"(.*?)"', obj, re.DOTALL)
        
        if id_match and title_match and desc_match:
            deeds.append({
                "id": int(id_match.group(1)),
                "title": title_match.group(1),
                "content": desc_match.group(1) + "\n\n(Full content will be available once the PDF is processed.)"
            })
            
    return deeds

def main():
    deeds = parse_data_js('data.js')
    print(f"Parsed {len(deeds)} deeds from data.js")
    
    with open('deeds_content.json', 'w', encoding='utf-8') as f:
        json.dump(deeds, f, indent=4)
        
    print("Generated deeds_content.json from data.js")

if __name__ == "__main__":
    main()

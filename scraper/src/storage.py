import json
import os

def save_data(data, filename="scholarships_data.json"):
    """
    Save the extracted data into a JSON file, appending to existing data if present.
    """
    if not data:
        print("[-] No valid data to save.")
        return
        
    existing_data = []
    
    # Read existing data if the file already exists
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            print("[!] Corrupted JSON file. Starting fresh.")
        except Exception as e:
            print(f"[!] Error reading existing data: {e}")
            
    # Deduplication loop
    urls_seen = {item.get('url') for item in existing_data}
    text_hashes_seen = {item.get('full_text_hash') for item in existing_data if item.get('full_text_hash')}
    
    new_data_count = 0
    for item in data:
        url = item.get('url')
        current_hash = item.get('full_text_hash')
        
        if url not in urls_seen and current_hash not in text_hashes_seen:
            existing_data.append(item)
            urls_seen.add(url)
            if current_hash:
                text_hashes_seen.add(current_hash)
            new_data_count += 1
    
    # Write back the deduplicated data
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
        print(f"[+] Successfully saved {new_data_count} UNIQUE new records to '{filename}'.")
        print(f"    Total unique records in file: {len(existing_data)}")
    except Exception as e:
        print(f"[!] Error saving data: {e}")

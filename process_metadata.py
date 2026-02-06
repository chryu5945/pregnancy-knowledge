import json
import os

RAW_FILE = "d:/개발/pregnancy_knowledge_system/data/full_list.json"
OUTPUT_FILE = "d:/개발/pregnancy_knowledge_system/data/videos.json"

def process():
    if not os.path.exists(RAW_FILE):
        print("Raw file not found")
        return

    try:
        with open(RAW_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except UnicodeDecodeError:
        # PowerShell redirection often creates UTF-16 LE
        with open(RAW_FILE, 'r', encoding='utf-16') as f:
            data = json.load(f)
    
    entries = data.get('entries', [])
    print(f"Found {len(entries)} entries.")
    
    # Load existing mock data to preserve transcripts if any match
    existing_transcripts = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            for item in old_data:
                # Map using title or some logic. 
                # Since mock IDs were 'mock_001', we can't map by ID.
                # We will just keep them as separate entries or drop them?
                # User asked for "full list", so real data is better.
                # I'll just keep the mock data at the top for testing RAG.
                pass

    processed_data = []
    
    # Add real videos
    for video in entries:
        video_id = video.get('id')
        title = video.get('title')
        url = video.get('url', f"https://www.youtube.com/watch?v={video_id}")
        description = video.get('description', '') # Get description
        
        processed_data.append({
            "id": video_id,
            "title": title,
            "url": url,
            "description": description,
            "transcript": [] 
        })
        
    # Prepend Mock Data so Search still works with something
    # (Or we can just rely on titles for now?)
    # Let's add the mock data efficiently.
    # Actually, let's just save the real data. 
    # NOTE: RAG search won't work well on empty transcripts, but List View will be populated.
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=4, ensure_ascii=False)
        
    print(f"Saved {len(processed_data)} videos to {OUTPUT_FILE}")

if __name__ == "__main__":
    process()

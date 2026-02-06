import json
import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATA_FILE = "d:/개발/pregnancy_knowledge_system/data/videos.json"
CHROMA_PATH = "d:/개발/pregnancy_knowledge_system/chroma_db"
COLLECTION_NAME = "pregnancy_knowledge"

def get_embedding_function():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    return embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_api_key,
        model_name="text-embedding-3-small"
    )

def chunk_transcript(transcript, chunk_size=500, overlap=50):
    """
    Chunks transcript into text blocks of roughly chunk_size characters.
    Uses transcript segments to maintain coherence.
    """
    chunks = []
    current_chunk = ""
    current_start = 0.0
    
    # Simple chunking strategy
    # Better strategy would be to respect sentence boundaries or time
    
    if not transcript:
        return []
        
    current_start = transcript[0]['start']
    
    for segment in transcript:
        text = segment['text']
        start = segment['start']
        
        if len(current_chunk) + len(text) > chunk_size:
            chunks.append({
                "text": current_chunk.strip(),
                "start": current_start
            })
            # Start new chunk with overlap (not implemented here for simplicity, just strict cut)
            # To add overlap, we would need to keep previous segments.
            # For now, let's just reset.
            current_chunk = text + " "
            current_start = start
        else:
            current_chunk += text + " "
            
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "start": current_start
        })
        
    return chunks

def build_db():
    if not os.path.exists(DATA_FILE):
        print(f"Data file {DATA_FILE} not found.")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        videos = json.load(f)
        
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embedding_fn = get_embedding_function()
    
    # Get or create collection
    # We delete it if it exists to rebuild clean
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except:
        pass
        
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )
    
    documents = []
    metadatas = []
    ids = []
    
    print(f"Processing {len(videos)} videos...")
    
    for i, video in enumerate(videos):
        video_id = video['id']
        title = video['title']
        url = video.get('url', f"https://www.youtube.com/watch?v={video_id}")
        transcript = video.get('transcript')
        description = video.get('description', '')
        
        # If transcript exists, chunk it
        if transcript:
            chunks = chunk_transcript(transcript)
            for j, chunk in enumerate(chunks):
                documents.append(chunk['text'])
                metadatas.append({
                    "video_id": video_id,
                    "title": title,
                    "url": url,
                    "start_time": chunk['start'],
                    "chunk_index": j,
                    "type": "transcript"
                })
                ids.append(f"{video_id}_t_{j}")
                
        # If no transcript but description exists, use description
        elif description:
            documents.append(f"제목: {title}\n\n설명: {description}")
            metadatas.append({
                "video_id": video_id,
                "title": title,
                "url": url,
                "start_time": 0.0,
                "chunk_index": 0,
                "type": "description"
            })
            ids.append(f"{video_id}_d_0")
        
        # If neither, just index title
        else:
             documents.append(f"제목: {title}")
             metadatas.append({
                "video_id": video_id,
                "title": title,
                "url": url,
                "start_time": 0.0,
                "chunk_index": 0,
                "type": "title_only"
            })
             ids.append(f"{video_id}_ti_0")
            
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1} videos.")

    # Add to collection in batches
    batch_size = 1000 # ChromaDB limit is usually higher but safe
    total_docs = len(documents)
    
    print(f"Adding {total_docs} chunks to database...")
    
    for k in range(0, total_docs, batch_size):
        end = min(k + batch_size, total_docs)
        collection.add(
            documents=documents[k:end],
            metadatas=metadatas[k:end],
            ids=ids[k:end]
        )
        print(f"Added batch {k} to {end}")
        
    print("Database build complete.")

if __name__ == "__main__":
    build_db()

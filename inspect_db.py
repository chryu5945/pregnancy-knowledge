import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = "d:/개발/pregnancy_knowledge_system/chroma_db"
COLLECTION_NAME = "pregnancy_knowledge"

def inspect():
    if not os.path.exists(CHROMA_PATH):
        print("ChromaDB path does not exist.")
        return

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        count = collection.count()
        print(f"Total documents in collection: {count}")
        
        if count > 0:
            print("\n--- Sample Document ---")
            results = collection.peek(limit=3)
            for i, doc in enumerate(results['documents']):
                meta = results['metadatas'][i]
                print(f"[{i}] Content: {doc[:100]}...")
                print(f"    Meta: {meta}")
        else:
            print("Collection is empty.")
            
    except Exception as e:
        print(f"Error accessing collection: {e}")

if __name__ == "__main__":
    inspect()

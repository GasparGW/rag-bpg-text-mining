import sys
import requests
from pathlib import Path

print("\n🧪 TEST RÁPIDO - RAG BPG")
print("="*50)

# Test 1: ChromaDB
print("\n1. Verificando ChromaDB...")
try:
    import chromadb
    db_path = Path("models/chroma_db")
    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_collection(name="bpg_manuals")
    print(f"✅ ChromaDB OK - {collection.count()} documentos")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Ollama
print("\n2. Verificando Ollama...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    modelos = [m['name'] for m in response.json().get('models', [])]
    print(f"✅ Ollama OK - Modelos: {modelos}")
except Exception as e:
    print(f"❌ Error: {e}")
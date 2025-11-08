# Archivo: ver_colecciones.py
import chromadb
from pathlib import Path

client = chromadb.PersistentClient(path="models/chroma_db")
colecciones = client.list_collections()

print("Colecciones en ChromaDB:")
for col in colecciones:
    print(f"  - {col.name} ({col.count()} docs)")
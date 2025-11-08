import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from tqdm import tqdm
import numpy as np
import shutil

# Rutas
CHUNKS_FILE = Path("data/processed/chunks.json")
CHROMA_DIR = Path("models/chroma_db")
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Configuración
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
COLLECTION_NAME = "bpg_manuals"

def load_chunks():
    """Carga chunks desde JSON"""
    print(f"📄 Cargando chunks desde {CHUNKS_FILE}")
    
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(f"No se encuentra el archivo {CHUNKS_FILE}")
    
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    if not chunks:
        raise ValueError("El archivo de chunks está vacío")
    
    print(f"✅ {len(chunks)} chunks cargados\n")
    return chunks

def initialize_embedding_model():
    """Inicializa modelo de embeddings"""
    print(f"🔧 Cargando modelo: {EMBEDDING_MODEL}")
    print("   (Primera vez puede tardar - descarga ~420 MB)")
    
    model = SentenceTransformer(EMBEDDING_MODEL)
    embedding_dim = model.get_sentence_embedding_dimension()
    
    print(f"✅ Modelo cargado")
    print(f"   Dimensiones: {embedding_dim}\n")
    
    return model, embedding_dim

def initialize_chromadb(embedding_dim):
    """Inicializa ChromaDB con limpieza completa"""
    print(f"💾 Inicializando ChromaDB en {CHROMA_DIR}")
    
    # Eliminar directorio completo para evitar problemas de metadata
    if CHROMA_DIR.exists():
        print("   Eliminando base de datos anterior...")
        shutil.rmtree(CHROMA_DIR)
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        print("   ✓ Base de datos anterior eliminada")
    
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Crear colección nueva con metadata explícita
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "Manuales BPG vectorizados",
            "hnsw:space": "cosine",
            "embedding_dimension": str(embedding_dim)
        }
    )
    
    print(f"✅ Colección '{COLLECTION_NAME}' creada")
    print(f"   Dimensión configurada: {embedding_dim}\n")
    return collection

def generate_and_store_embeddings(chunks, model, collection):
    """Genera embeddings y los guarda en ChromaDB"""
    print("🔢 Generando embeddings...")
    
    texts = [chunk['text'] for chunk in chunks]
    chunk_ids = [chunk['chunk_id'] for chunk in chunks]
    
    # Validar que no haya IDs duplicados
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Hay chunk_ids duplicados en los datos")
    
    # Generar embeddings en batch (más eficiente)
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        convert_to_numpy=True
    )
    
    print(f"\n✅ {len(embeddings)} embeddings generados")
    print(f"   Forma: {embeddings.shape}")
    print(f"   Tipo: {type(embeddings)}\n")
    
    # Preparar metadata
    metadatas = []
    for chunk in chunks:
        metadatas.append({
            "source": chunk['source'],
            "chunk_number": chunk['chunk_number'],
            "total_chunks": chunk['total_chunks'],
            "word_count": chunk['word_count']
        })
    
    # Guardar en ChromaDB
    print("💾 Guardando en ChromaDB...")
    
    collection.add(
        ids=chunk_ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas
    )
    
    stored_count = collection.count()
    print(f"✅ {stored_count} vectores guardados en ChromaDB")
    
    if stored_count != len(chunks):
        print(f"⚠️  ADVERTENCIA: Se esperaban {len(chunks)} vectores, pero se guardaron {stored_count}")
    print()

def verify_storage(collection, model):
    """Verifica que los datos se guardaron correctamente"""
    print("🔍 Verificando almacenamiento...")
    
    # Verificar conteo
    stored_count = collection.count()
    print(f"   Documentos en colección: {stored_count}")
    
    if stored_count == 0:
        raise ValueError("La colección está vacía después de guardar")
    
    # Generar embedding para la query con el mismo modelo
    query_text = "vacunación ganado bovino"
    print(f"   Generando embedding para query de prueba...")
    
    query_embedding = model.encode([query_text], convert_to_numpy=True)
    print(f"   Embedding generado - dimensión: {query_embedding.shape}")
    
    # Test query usando el embedding generado
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=min(3, stored_count)
    )
    
    print(f"\n✅ Verificación exitosa")
    print(f"\n📝 Test query: '{query_text}'")
    print(f"   Top {len(results['documents'][0])} chunks recuperados:")
    
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        print(f"\n   {i}. Fuente: {metadata['source']}")
        print(f"      Chunk: {metadata['chunk_number']}/{metadata['total_chunks']}")
        print(f"      Preview: {doc[:100]}...")

def main():
    """Pipeline principal"""
    print("=" * 60)
    print("🚀 GENERACIÓN DE EMBEDDINGS Y ALMACENAMIENTO VECTORIAL")
    print("=" * 60 + "\n")
    
    try:
        # 1. Cargar chunks
        chunks = load_chunks()
        
        # 2. Inicializar modelo embeddings
        model, embedding_dim = initialize_embedding_model()
        
        # 3. Inicializar ChromaDB
        collection = initialize_chromadb(embedding_dim)
        
        # 4. Generar y guardar embeddings
        generate_and_store_embeddings(chunks, model, collection)
        
        # 5. Verificar
        verify_storage(collection, model)
        
        print("\n" + "=" * 60)
        print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\n📊 Resumen:")
        print(f"   • Chunks procesados: {len(chunks)}")
        print(f"   • Vectores en ChromaDB: {collection.count()}")
        print(f"   • Dimensión embeddings: {embedding_dim}")
        print(f"   • Ubicación: {CHROMA_DIR}")
        print(f"   • Modelo: {EMBEDDING_MODEL}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
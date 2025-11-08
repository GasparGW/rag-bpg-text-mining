import json
from pathlib import Path
import re

# Rutas
PROCESSED_DIR = Path("data/processed")
CHUNKS_OUTPUT = PROCESSED_DIR / "chunks.json"

# Parámetros
TARGET_WORDS = 500
OVERLAP_WORDS = 50

def split_into_sentences(text):
    """Divide texto en oraciones"""
    # Regex simple para español
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def count_words(text):
    """Cuenta palabras en texto"""
    return len(text.split())

def create_chunks_recursive(text, target_words=TARGET_WORDS, overlap_words=OVERLAP_WORDS):
    """
    Crea chunks recursivos con overlap
    
    Estrategia:
    1. Intentar dividir por párrafos (\n\n)
    2. Si muy grande, por líneas (\n)
    3. Si muy grande, por oraciones (.)
    4. Agregar overlap entre chunks
    """
    chunks = []
    
    # Dividir por párrafos primero
    paragraphs = text.split('\n\n')
    
    current_chunk = []
    current_word_count = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        para_words = count_words(para)
        
        # Si párrafo solo ya es muy grande, dividir por oraciones
        if para_words > target_words:
            sentences = split_into_sentences(para)
            for sent in sentences:
                sent_words = count_words(sent)
                
                if current_word_count + sent_words <= target_words:
                    current_chunk.append(sent)
                    current_word_count += sent_words
                else:
                    # Guardar chunk actual
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    
                    # Overlap: últimas palabras del chunk anterior
                    overlap_text = ' '.join(current_chunk[-3:]) if len(current_chunk) >= 3 else ''
                    
                    # Nuevo chunk con overlap
                    current_chunk = [overlap_text, sent] if overlap_text else [sent]
                    current_word_count = count_words(' '.join(current_chunk))
        
        # Si párrafo cabe en chunk actual
        elif current_word_count + para_words <= target_words:
            current_chunk.append(para)
            current_word_count += para_words
        
        # Si no cabe, crear nuevo chunk
        else:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            # Overlap
            overlap_text = ' '.join(current_chunk[-3:]) if len(current_chunk) >= 3 else ''
            current_chunk = [overlap_text, para] if overlap_text else [para]
            current_word_count = count_words(' '.join(current_chunk))
    
    # Agregar último chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def process_documents():
    """Procesa todos los .txt y genera chunks"""
    
    txt_files = list(PROCESSED_DIR.glob("*.txt"))
    
    if not txt_files:
        print("❌ No hay archivos .txt en data/processed/")
        return
    
    print(f"📄 Procesando {len(txt_files)} documentos\n")
    
    all_chunks = []
    
    for txt_file in txt_files:
        print(f"Chunking: {txt_file.name}")
        
        # Leer texto
        with open(txt_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Crear chunks
        chunks = create_chunks_recursive(text)
        
        # Agregar metadata
        for i, chunk_text in enumerate(chunks, 1):
            chunk_data = {
                "chunk_id": f"{txt_file.stem}_{i}",
                "source": txt_file.stem,
                "text": chunk_text,
                "word_count": count_words(chunk_text),
                "chunk_number": i,
                "total_chunks": len(chunks)
            }
            all_chunks.append(chunk_data)
        
        print(f"  ✅ {len(chunks)} chunks creados")
        print(f"  📊 Promedio: {sum(count_words(c) for c in chunks) / len(chunks):.0f} palabras/chunk\n")
    
    # Guardar todos los chunks
    with open(CHUNKS_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"🎉 Total: {len(all_chunks)} chunks guardados en {CHUNKS_OUTPUT}")

if __name__ == "__main__":
    process_documents()
import os
import pdfplumber
from pathlib import Path

# Rutas
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extrae texto de un PDF usando pdfplumber"""
    print(f"Procesando: {pdf_path.name}")
    
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
            
            if i % 10 == 0:
                print(f"  Páginas procesadas: {i}/{len(pdf.pages)}")
    
    return text

def clean_text(text):
    """Limpieza básica del texto"""
    # Eliminar múltiples saltos de línea
    text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
    return text

def main():
    # Buscar todos los PDFs en raw/
    pdf_files = list(RAW_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No se encontraron PDFs en data/raw/")
        return
    
    print(f"📄 Encontrados {len(pdf_files)} PDFs\n")
    
    for pdf_path in pdf_files:
        try:
            # Extraer texto
            text = extract_text_from_pdf(pdf_path)
            
            # Limpiar
            text = clean_text(text)
            
            # Guardar
            output_path = PROCESSED_DIR / f"{pdf_path.stem}.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            print(f"✅ Guardado: {output_path.name}")
            print(f"   Caracteres: {len(text):,}\n")
            
        except Exception as e:
            print(f"❌ Error procesando {pdf_path.name}: {e}\n")
    
    print("🎉 Proceso completado!")

if __name__ == "__main__":
    main()
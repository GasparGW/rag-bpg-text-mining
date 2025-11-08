# Carpeta DATA

## raw/
Datos originales SIN modificar:
- PDFs manuales BPG (AIGuiadeBuenasPracticasGanaderasenFEEDLOTV2022.pdf, etc.)
- Encuestas originales (eval.csv, AUTOEVALUACIÓN.xlsx)
- Cualquier otro documento fuente

⚠️ **NUNCA subir a Git**

## processed/
Datos procesados pero NO anonimizados:
- Textos extraídos de PDFs
- Chunks de texto
- Embeddings intermedios

⚠️ **NUNCA subir a Git**

## anonymized/
Datos ofuscados, sin información sensible:
- Encuestas anonimizadas
- Logs sin datos personales
- Datos seguros para compartir

✅ **ÚNICO directorio que se puede subir a Git**

# Guía de Setup - RAG BPG

## 1️⃣ Instalación Inicial

### En tu máquina local (VS Code):

```bash
# 1. Clonar/crear carpeta del proyecto
cd ruta/donde/quieras/el/proyecto
mkdir rag-bpg-project
cd rag-bpg-project

# 2. Crear entorno virtual Python
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

## 2️⃣ Obtener API Keys

### Claude (Anthropic):
1. Ir a: https://console.anthropic.com/
2. Crear cuenta / Login
3. API Keys → Create Key
4. Copiar en `.env` → `ANTHROPIC_API_KEY`

### OpenAI (opcional):
1. Ir a: https://platform.openai.com/
2. API Keys → Create new secret key
3. Copiar en `.env` → `OPENAI_API_KEY`

### Hugging Face (para embeddings):
1. Ir a: https://huggingface.co/settings/tokens
2. Create new token (read)
3. Copiar en `.env` → `HF_TOKEN`

## 3️⃣ Verificar Instalación

```bash
# Test básico
python -c "import transformers; import chromadb; print('✅ Todo OK')"
```

## 4️⃣ Estructura Git

```bash
# Inicializar Git
git init

# Agregar archivos
git add .
git commit -m "Initial commit: Project structure"

# VERIFICAR antes de push:
git status
# NO debe aparecer data/raw/ ni data/processed/
```

## 5️⃣ Próximos Pasos

1. Poner PDFs BPG en `data/raw/`
2. Poner encuestas en `data/raw/`
3. Leer notebooks de la cátedra
4. Empezar con anonimización

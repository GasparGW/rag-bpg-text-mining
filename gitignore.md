
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual Environment
venv/
env/
ENV/

# Ollama Models (locales, no subir)
*.gguf
*.bin

# ChromaDB
models/chroma_db/*.sqlite3
models/chroma_db/*.parquet

# Logs
*.log
*.out

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Backups
*.backup
backups/

# Test outputs
test_output/
*.pytest_cache/

# Sensitive
.env
secrets/
*.key
*.pem
EOF

echo "✅ .gitignore actualizado"
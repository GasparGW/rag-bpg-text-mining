# Guía Git - Comandos Útiles

## Setup Inicial

```bash
# Inicializar repositorio
git init

# Configurar usuario (primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# Primer commit
git add .
git commit -m "feat: Initial project structure"
```

## Workflow Diario

```bash
# Ver estado
git status

# Agregar cambios
git add archivo.py                  # Un archivo específico
git add src/                        # Una carpeta
git add .                           # Todo

# Commit
git commit -m "feat: Descripción del cambio"

# Ver historial
git log --oneline

# Ver cambios antes de commit
git diff
```

## ⚠️ ANTES de Hacer Push

```bash
# SIEMPRE verificar que NO subas datos sensibles:
git status

# Buscar archivos que no deberían estar:
git ls-files | grep "data/raw"      # NO debería aparecer nada
git ls-files | grep "data/processed" # NO debería aparecer nada
git ls-files | grep ".env"          # NO debería aparecer (solo .env.example)
```

## Tipos de Commits (Convención)

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `refactor:` Refactorización de código
- `test:` Agregar tests
- `chore:` Tareas mantenimiento

## Ramas (Avanzado)

```bash
# Crear rama nueva
git checkout -b feature/anonimizacion

# Cambiar de rama
git checkout main

# Mergear rama
git merge feature/anonimizacion
```

## Subir a GitHub

```bash
# Primera vez (crear repo en GitHub primero)
git remote add origin https://github.com/tu-usuario/rag-bpg.git
git push -u origin main

# Siguientes veces
git push
```

## 🔒 Seguridad

**NUNCA hacer push de:**
- Archivos en `data/raw/`
- Archivos en `data/processed/`
- Archivo `.env` (solo `.env.example`)
- API keys
- Datos personales

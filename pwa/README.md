# 🌐 BPG Consultas - Progressive Web App

Sistema de consultas sobre Buenas Prácticas Ganaderas con funcionalidad **offline completa**, ideal para uso en el campo sin conexión a internet.

## 🎯 Características

### Funcionalidad Principal
- ✅ **Consultas RAG** sobre Buenas Prácticas Ganaderas
- ✅ **Funciona sin internet** (Service Worker + IndexedDB)
- ✅ **Instalable** como aplicación nativa
- ✅ **Responsive** (móvil, tablet, desktop)
- ✅ **Historial offline** con búsqueda inteligente
- ✅ **Caché automático** de respuestas

### Tecnologías
- **Frontend:** Vanilla JavaScript (ES6+)
- **Storage:** IndexedDB para historial offline
- **Offline:** Service Worker con estrategia Cache-First/Network-First
- **API:** RESTful backend (FastAPI)
- **UI:** CSS moderno con variables, responsive, animaciones

---

## 🚀 Instalación y Uso

### Prerrequisitos

1. **Backend API corriendo:**
```bash
   cd ~/Desktop/rag-bpg-project
   source venv/bin/activate
   python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

2. **Servidor HTTP para PWA:**
```bash
   python3 -m http.server 8080 --directory pwa
```

### Acceso Web

Abrir en navegador:
```
http://localhost:8080
```

### Instalación como App

#### Desktop (Chrome/Edge):
1. Click en botón **"📲 Instalar App"** (amarillo, arriba derecha)
2. Confirmar instalación en popup
3. La app se abrirá en ventana independiente

#### Móvil (Android):
1. Abrir en Chrome
2. Menú → **"Agregar a pantalla de inicio"**
3. Confirmar

#### Móvil (iOS/Safari):
1. Abrir en Safari
2. Botón compartir → **"Agregar a pantalla de inicio"**
3. Confirmar

---

## 💻 Uso

### Consulta Básica

1. Escribir pregunta en el textarea
2. Click **"Consultar"**
3. Esperar respuesta (~60s con llama3.1:8b)
4. Ver respuesta con metadata

### Opciones Avanzadas

Click en **"⚙️ Opciones Avanzadas"** para:
- **Estrategia:** Standard, Concise, Few-Shot, Technical
- **Documentos (k):** Cantidad de chunks a recuperar (1-10)

### Modo Offline

**Automático:** La app detecta cuando no hay conexión y:
- Status cambia a **"Sin conexión"**
- Usa respuestas cacheadas del historial
- Banner amarillo indica: "📦 Respuesta recuperada de caché"

### Historial

**Todas las consultas se guardan localmente (IndexedDB):**
- Scroll a sección **"📚 Historial (Offline)"**
- Click en cualquier item para recargar respuesta
- Botón **"🗑️ Limpiar"** para borrar todo

---

## 🏗️ Arquitectura

### Estructura de Archivos
```
pwa/
├── index.html          # UI principal
├── manifest.json       # Config PWA (instalación)
├── sw.js              # Service Worker (offline)
├── css/
│   └── styles.css     # Estilos responsive
├── js/
│   ├── app.js         # Lógica principal
│   └── db.js          # IndexedDB manager
└── icons/
    ├── icon-192.png
    └── icon-512.png
```

### Flujo de Datos
```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│         app.js                  │
│  - Maneja UI                    │
│  - Detecta online/offline       │
│  - Decide: API o caché          │
└──────┬──────────────────┬───────┘
       │                  │
       ▼                  ▼
┌─────────────┐    ┌─────────────┐
│   API REST  │    │ IndexedDB   │
│ (online)    │    │ (offline)   │
└─────────────┘    └─────────────┘
       │                  │
       └────────┬─────────┘
                ▼
         ┌─────────────┐
         │  Respuesta  │
         └─────────────┘
```

### Service Worker - Estrategias

**Cache First (Archivos estáticos):**
```javascript
Cache → Red (fallback)
// HTML, CSS, JS, imágenes
```

**Network First (API):**
```javascript
Red → Cache (fallback)
// Llamadas a /api/v1/*
```

---

## 🔧 Configuración

### API Endpoint

Modificar en `js/app.js` línea 10:
```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',  // ← Cambiar según deployment
    API_TIMEOUT: 120000,
    MAX_HISTORY_ITEMS: 50
};
```

### Manifest PWA

Editar `manifest.json` para:
- Nombre de app
- Colores
- Iconos
- Start URL

### Service Worker

`sw.js` línea 7:
```javascript
const CACHE_NAME = 'bpg-consultas-v2.1';  // ← Incrementar para forzar actualización
```

---

## 📱 Testing

### Test 1: Funcionalidad Básica

1. Abrir `http://localhost:8080`
2. Hacer consulta: "¿Qué es el bienestar animal?"
3. Verificar respuesta completa

### Test 2: Offline

1. **DevTools (F12)** → **Network** → **Offline**
2. Recargar página (debe cargar desde caché)
3. Hacer consulta (debe usar historial)
4. Verificar banner "📦 Respuesta recuperada de caché"

### Test 3: Service Worker

1. **DevTools** → **Application** → **Service Workers**
2. Verificar: `✅ activated and is running`

### Test 4: Storage

1. **DevTools** → **Application** → **IndexedDB** → **BPGConsultas**
2. Ver tabla `history` con consultas guardadas

### Test 5: Instalación

1. Click **"📲 Instalar App"**
2. Abrir app instalada
3. Verificar funciona sin navegador

---

## 🐛 Troubleshooting

### Botón "Instalar App" no aparece

**Causas:**
- Ya está instalada
- Criterios PWA no cumplidos
- Service Worker no activo

**Solución:**
```bash
# Desinstalar app
chrome://apps → Click derecho → Eliminar

# Verificar manifest.json válido
# Verificar HTTPS (producción) o localhost (desarrollo)
```

### Página no carga offline

**Causas:**
- Service Worker no activado
- Archivos no cacheados

**Solución:**
```javascript
// DevTools → Application → Service Workers
// Click "Update" para forzar actualización
// O incrementar CACHE_NAME en sw.js
```

### Consulta offline falla

**Causas:**
- No hay consultas similares en historial
- IndexedDB bloqueada

**Solución:**
- Hacer al menos una consulta online primero
- Verificar storage en DevTools → Application → Storage

### Error 404 en app instalada

**Causa:** `start_url` incorrecto en manifest.json

**Solución:**
```json
// manifest.json
"start_url": "/",  // NO "/pwa/"
"scope": "/"
```

---

## 🚀 Deployment

### Producción (con HTTPS)

**Requisitos:**
- Dominio con HTTPS (obligatorio para PWA)
- Servidor web (Nginx, Apache, o similar)
- API accesible

**Pasos:**

1. **Actualizar API endpoint:**
```javascript
   // js/app.js
   API_BASE_URL: 'https://tu-dominio.com'
```

2. **Actualizar manifest.json:**
```json
   "start_url": "https://tu-dominio.com/",
   "scope": "https://tu-dominio.com/"
```

3. **Subir archivos:**
```bash
   # Copiar carpeta pwa/ a servidor
   scp -r pwa/ usuario@servidor:/var/www/html/
```

4. **Configurar HTTPS:**
```nginx
   # Nginx example
   server {
       listen 443 ssl;
       server_name tu-dominio.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           root /var/www/html/pwa;
           try_files $uri $uri/ /index.html;
       }
   }
```

### Vercel/Netlify (Simple)

**vercel.json:**
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**Deployment:**
```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
cd pwa
vercel --prod
```

---

## 📊 Performance

### Métricas

| Métrica | Valor | Objetivo |
|---------|-------|----------|
| **First Load** | ~500ms | < 1s |
| **Offline Load** | ~100ms | < 200ms |
| **Query (online)** | 5-60s | Depende del LLM |
| **Query (offline)** | ~50ms | < 100ms |
| **Storage Usage** | ~2MB | < 50MB |

### Optimizaciones

**Implementadas:**
- ✅ Minificación CSS (variables, reutilización)
- ✅ Caché agresivo de estáticos
- ✅ Lazy loading de historial
- ✅ Debounce en character counter

**Posibles mejoras futuras:**
- Comprimir respuestas en IndexedDB
- Virtual scrolling en historial largo
- Code splitting (si crece complejidad)

---

## 🔐 Seguridad

### Consideraciones

**Implementado:**
- ✅ Escape HTML en historial (XSS prevention)
- ✅ CORS configurado en API
- ✅ Validación de inputs (Pydantic en backend)
- ✅ HTTPS requerido en producción

**Recomendaciones producción:**
- Agregar rate limiting en API
- Autenticación si es privado
- CSP headers
- Sanitización adicional de respuestas LLM

---

## 📈 Analytics (Futuro)

Para trackear uso en producción:
```javascript
// js/app.js - Agregar después de línea 500

// Google Analytics
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'GA_MEASUREMENT_ID');

// Track queries
gtag('event', 'query', {
    'event_category': 'engagement',
    'event_label': STATE.isOnline ? 'online' : 'offline'
});
```

---

## 🤝 Contribuir

### Setup Desarrollo
```bash
# Clonar repo
git clone <repo-url>
cd rag-bpg-project

# Instalar dependencias backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Correr API
python3 -m uvicorn api.main:app --reload --port 8000

# Correr PWA (otra terminal)
python3 -m http.server 8080 --directory pwa
```

### Estilo de Código

- **JavaScript:** ES6+, sin transpiler
- **CSS:** Variables CSS, BEM naming
- **Commits:** Conventional commits

### Agregar Features

**Ejemplo: Nueva estrategia de prompt**

1. Backend: Agregar en `prompts/strategies.py`
2. Frontend: Agregar opción en `index.html` línea 68
3. Probar ambos modos (online/offline)

---

## 📄 Licencia

[Tu licencia aquí]

---

## 👥 Autores

Sistema RAG BPG v2.1  
PWA: Noviembre 2025  

---

## 📞 Soporte

**Problemas comunes:** Ver sección Troubleshooting  
**Issues:** [GitHub Issues]  
**Docs API:** http://localhost:8000/docs  

---

**🎉 ¡Gracias por usar BPG Consultas PWA!**

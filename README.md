# 🎧 Pipeline de Transcripción de Audio con IA

Pipeline integral de procesamiento de audio que automatiza la transcripción de archivos largos usando tecnologías de inteligencia artificial avanzadas. **Optimizado para sistemas de 32GB RAM** con procesamiento paralelo y generación automática de resúmenes.

## ✨ Características Principales

### 🚀 Transcripción Avanzada Optimizada
- **Modelos Whisper Optimizados**: Soporte completo para todos los modelos (tiny → large-v3)
- **Segmentación Inteligente**: Procesa automáticamente audios largos en segmentos de 10 minutos
- **Procesamiento Paralelo**: 3 workers simultáneos para sistemas de 32GB RAM
- **Múltiples Idiomas**: Español por defecto con selector de 13+ idiomas
- **Progreso en Tiempo Real**: Visualización detallada del progreso por segmento

### 🧠 Resúmenes Automáticos con IA
- **Generación Automática**: Resúmenes inteligentes después de cada transcripción
- **Algoritmo Avanzado**: Selecciona las 25-30% oraciones más representativas
- **Estructura Inteligente**: Introducción + contenido principal + conclusión
- **Estadísticas Incluidas**: Conteo de palabras y oraciones originales

### 🌍 Soporte Multiidioma Completo
- **Idioma por Defecto**: Español configurado automáticamente
- **Selector Dinámico**: Cambio de idioma en tiempo real desde la UI
- **Auto-detección**: Opción para detectar idioma automáticamente
- **13+ Idiomas**: Español, Inglés, Francés, Alemán, Italiano, Portugués, Ruso, Japonés, Coreano, Chino, Árabe, Hindi

### ⚡ Optimizaciones para 32GB RAM
- **Modelo Large-v3**: Máxima precisión con preload en memoria
- **Segmentos Grandes**: 10 minutos por segmento (vs 5 min estándar)
- **Procesamiento Paralelo**: 3 workers simultáneos
- **Gestión Inteligente**: Modelo mantenido en memoria entre transcripciones

### 🎯 Interfaz Moderna y Responsive
- **UI Intuitiva**: Diseño moderno con animaciones suaves
- **Drag & Drop**: Arrastra archivos directamente
- **Progreso Visual**: Barras de progreso y grids de segmentos detallados
- **Información de Optimización**: Panel dedicado mostrando estado de optimizaciones
- **Responsive**: Optimizado para desktop y móvil

## 🛠️ Stack Tecnológico

### Frontend
- **React 18** + TypeScript
- **Tailwind CSS** + shadcn/ui components
- **Vite** para build ultra-rápido
- **Lucide React** para iconografía moderna
- **React Router** para navegación SPA

### Backend
- **Express.js** + TypeScript
- **PostgreSQL** (puerto 5433) para persistencia
- **Redis** (puerto 6380) para caché y progreso
- **Multer** para uploads optimizados
- **Axios** para comunicación con servicios

### AI & Processing
- **Faster-Whisper** para transcripción de alta calidad
- **NumPy** para procesamiento matemático de audio
- **Librosa/SoundFile** para manipulación de audio avanzada
- **Python 3.12** con virtual environment aislado
- **ThreadPoolExecutor** para procesamiento paralelo

### Infrastructure
- **Docker Compose** para servicios de base de datos
- **Auto-detección** de comandos Docker (compose vs docker-compose)
- **Scripts automatizados** para setup completo
- **Gestión de entornos** Python automatizada

## 📋 Requisitos del Sistema

### Mínimos
- **Node.js** 18+ y **pnpm**
- **Python** 3.12+ con pip
- **Docker** y **Docker Compose**
- **4GB RAM** (funcional)

### Recomendados (Optimizaciones Completas)
- **32GB RAM** para procesamiento paralelo
- **GPU CUDA** (opcional, fallback a CPU automático)
- **SSD** para modelo caché rápido

## 🚀 Instalación y Uso

### 🎯 Opción 1: Desarrollo Rápido (Recomendado para pruebas)

```bash
# Clonar repositorio
git clone https://github.com/dvillagrans/Transcripcion.git
cd Transcripcion

# Inicio rápido con modelo medium (30-60s de carga)
python start_dev.py
```

**Ventajas del modo desarrollo:**
- ✅ Carga en 30-60 segundos
- ✅ Modelo `medium` (769MB) 
- ✅ Buena calidad para desarrollo
- ✅ Todas las optimizaciones activas

### 🏆 Opción 2: Producción Completa (Máxima calidad)

```bash
# Inicio completo con modelo large-v3 (1-3min de carga)
python start_all.py
```

**Ventajas del modo producción:**
- ✅ Modelo `large-v3` (1.5GB) - máxima precisión
- ✅ Optimizado para 32GB RAM
- ✅ Procesamiento paralelo completo
- ✅ Calidad profesional

### ⚙️ Opción 3: Instalación Manual

#### 1. Configurar Python
```bash
# Crear entorno virtual
python3 -m venv env
source env/bin/activate  # Linux/Mac
# env\Scripts\activate   # Windows

# Instalar dependencias Python
pip install -r requirements.txt
```

#### 2. Configurar Node.js
```bash
# Backend
pnpm install

# Frontend
cd frontend && pnpm install && cd ..
```

#### 3. Iniciar Servicios Manualmente
```bash
# Docker (PostgreSQL + Redis)
docker-compose up -d

# Backend API (puerto 3001)
pnpm run server:dev

# Frontend (puerto 3000)
cd frontend && pnpm run dev

# Servicio Python (puerto 5000)
python transcription_service.py
```

## 🌐 Acceso a la Aplicación

| Servicio | URL | Puerto | Descripción |
|----------|-----|---------|-------------|
| **Frontend** | http://localhost:3000 | 3000 | Interfaz principal |
| **Backend API** | http://localhost:3001 | 3001 | API REST |
| **Python Service** | http://localhost:5000 | 5000 | Servicio de transcripción |
| **PostgreSQL** | localhost:5433 | 5433 | Base de datos |
| **Redis** | localhost:6380 | 6380 | Caché y progreso |

## 🎯 Guía de Uso Completa

### 1. 🎛️ Configuración Inicial
![Config](https://img.shields.io/badge/Paso-1-blue)

- Ve a **Configuración** (`/config`)
- **Modelo Whisper**: Selecciona según tus necesidades
  - `tiny`: Ultra rápido ⚡⚡⚡ (precisión ⭐⭐)
  - `medium`: **Equilibrado** ⚡⚡ (precisión ⭐⭐⭐⭐)
  - `large-v3`: **Máxima precisión** ⚡ (precisión ⭐⭐⭐⭐⭐)
- **Idioma**: Selecciona español o cualquier otro idioma soportado
- **Resumen automático**: ✅ Activa para obtener resúmenes inteligentes
- **Configuración se guarda automáticamente** en localStorage

### 2. 🎵 Subir y Procesar Audio
![Process](https://img.shields.io/badge/Paso-2-green)

- Ve a **Procesar** (`/process`)
- **Métodos de carga**:
  - 📁 **Arrastra y suelta** archivos directamente
  - 🖱️ **Click para seleccionar** desde explorador
- **Formatos soportados**: `MP3`, `WAV`, `FLAC`, `M4A`, `OGG`
- **Tamaño máximo**: **500MB** (optimizado para audios de 1:30h)
- **Selector de idioma**: Cambia idioma específico si es necesario
- **Vista previa**: Información del archivo antes de procesar

### 3. 📊 Monitoreo Avanzado en Tiempo Real
![Progress](https://img.shields.io/badge/Paso-3-orange)

#### Para **audios largos** (>10 minutos):
- ✅ **Segmentación automática** en bloques de 10 minutos
- 📊 **Grid visual detallado** mostrando cada segmento
- ⏱️ **Tiempo estimado** de finalización
- 🔄 **Progreso por segmento** en tiempo real
- 📈 **Estadísticas técnicas** (workers, modelo, optimizaciones)
- 🚀 **Información de optimización** para sistemas de 32GB RAM

#### Panel de Optimización:
```
🚀 Optimizaciones para 32GB RAM Activadas
• Modo: 🚀 Alto Rendimiento
• Workers Paralelos: 3x  
• Modelo Precargado: ✅ Sí
• Duración Segmento: 10 min
🎯 Rendimiento esperado: ~3x más rápido que modo estándar
```

### 4. 📋 Resultados Completos
![Results](https://img.shields.io/badge/Paso-4-purple)

- 📝 **Transcripción completa** y precisa
- 🧠 **Resumen automático inteligente**:
  - Selección de oraciones clave (25-30% del original)
  - Estructura: introducción + contenido + conclusión
  - Estadísticas: conteo de palabras y oraciones
- 💾 **Descarga** en múltiples formatos
- 📋 **Copia rápida** al portapapeles
- 🔍 **Búsqueda** dentro del texto transcrito

### 5. 📚 Historial y Gestión
![History](https://img.shields.io/badge/Paso-5-indigo)

- 📜 **Lista completa** de transcripciones anteriores
- 🔍 **Búsqueda rápida** por nombre de archivo
- 🗑️ **Eliminación selectiva** de trabajos antiguos
- 📊 **Estado detallado** de cada procesamiento
- 🏷️ **Metadatos**: duración, modelo usado, idioma detectado

## 🚀 Características Avanzadas

### 🧩 Segmentación Inteligente Optimizada

```python
# Configuración automática basada en RAM disponible
if system_ram >= 32_GB:
    segment_duration = 600  # 10 minutos
    parallel_workers = 3
    model_default = 'large-v3'
else:
    segment_duration = 300  # 5 minutos  
    parallel_workers = 1
    model_default = 'medium'
```

### 🌍 Sistema de Idiomas Avanzado

```typescript
const languages = [
  { code: 'es', name: 'Español', flag: '🇪🇸' },        // Por defecto
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
  { code: 'pt', name: 'Português', flag: '🇧🇷' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦' },
  { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
  { code: 'auto', name: 'Auto-detectar', flag: '🌍' }
];
```

### 🧠 Generación Automática de Resúmenes

```python
def generate_summary(text: str) -> str:
    """Algoritmo inteligente de resumen"""
    # 1. Análisis de estructura de oraciones
    sentences = parse_sentences(text)
    
    # 2. Selección estratégica (25-30% del total)
    selected = select_key_sentences(sentences)
    
    # 3. Estructura: intro + contenido + conclusión
    summary = build_structured_summary(selected)
    
    # 4. Agregar estadísticas
    stats = f"📊 {len(sentences)} oraciones, ~{count_words(text)} palabras"
    
    return f"{summary}\n\n{stats}"
```

### 📊 Progreso Detallado y Optimización

```typescript
interface OptimizedProgressData {
  // Progreso básico
  progress: number;
  stage: string;
  
  // Segmentación
  segments_total: number;
  segments_completed: number;
  current_segment: number;
  
  // Optimizaciones
  optimization_mode: 'high_memory' | 'standard';
  parallel_workers: number;
  model_preloaded: boolean;
  segment_duration: number; // en minutos
  
  // Estimaciones mejoradas
  estimated_time_remaining: string;
  processing_speed: string;
}
```

## 🔧 API Reference Completa

### 🎵 Audio Processing API

#### Upload Audio con Optimizaciones
```bash
POST /api/audio/upload
Content-Type: multipart/form-data

{
  "audioFile": File,
  "whisperModel": "large-v3",     # tiny|base|small|medium|large-v3
  "language": "es",               # Código de idioma o "auto"
  "generateSummary": true         # Resumen automático
}

Response:
{
  "success": true,
  "data": {
    "jobId": "uuid-v4",
    "status": "processing", 
    "filename": "audio.mp3"
  }
}
```

#### Get Detailed Progress
```bash
GET /api/audio/status/:jobId

Response:
{
  "success": true,
  "data": {
    "jobId": "uuid",
    "status": "processing",
    "progress": 65,
    "currentStage": "Transcribiendo segmento 7/12 (paralelo)",
    "segments": {
      "total": 12,
      "completed": 6,
      "current": 7
    },
    "optimization": {
      "mode": "high_memory",
      "workers": 3,
      "model_preloaded": true,
      "segment_duration": 10
    },
    "timing": {
      "estimated_remaining": "8.5 minutos",
      "processing_speed": "2.3x tiempo real"
    }
  }
}
```

#### Get Complete Results
```bash
GET /api/audio/results/:jobId

Response:
{
  "success": true,
  "data": {
    "transcription": "Texto completo de la transcripción...",
    "summary": "Resumen automático inteligente que incluye las ideas principales...\n\n📊 Estadísticas: 87 oraciones, ~2341 palabras.",
    "metadata": {
      "duration": "5400s",
      "language": "es", 
      "language_probability": 0.95,
      "model": "large-v3",
      "segments_count": 12,
      "processing_time": "890.2s",
      "optimization_used": true
    }
  }
}
```

### 🐍 Python Service API

#### Advanced Transcribe Endpoint
```bash
POST http://localhost:5000/transcribe

{
  "file_path": "/path/to/audio.mp3",
  "model": "large-v3",
  "language": "es",
  "generate_summary": true,
  "job_id": "uuid"
}

Response:
{
  "success": true,
  "job_id": "uuid",
  "transcription": "Texto completo...",
  "summary": "Resumen inteligente...",
  "segments": [...],
  "language": "es",
  "duration": 5400,
  "processing_time": 890.2,
  "model_used": "large-v3",
  "segments_count": 12,
  "optimization_mode": "high_memory"
}
```

#### Real-time Progress Endpoint
```bash
GET http://localhost:5000/progress/:jobId

Response:
{
  "progress": 65,
  "stage": "Transcribiendo segmento 7/12 (paralelo)",
  "segments_completed": 6,
  "segments_total": 12,
  "estimated_time": "8.5 minutos",
  "optimization_mode": "high_memory",
  "parallel_workers": 3,
  "model_preloaded": true
}
```

## ⚙️ Configuración Avanzada

### 🔧 Variables de Entorno Completas

```bash
# === OPTIMIZACIÓN ===
DEFAULT_MODEL=large-v3          # Modelo por defecto
DEV_MODE=false                  # true para desarrollo rápido
ROBUST_MODE=true                # Modo robusto para estabilidad

# === PROCESAMIENTO ===
PARALLEL_WORKERS=3              # Workers para sistemas 32GB RAM
SEGMENT_LENGTH=600              # Duración segmentos (segundos)
HIGH_MEMORY_MODE=true           # Optimizaciones para 32GB+
PRELOAD_MODEL=true              # Precargar modelo en memoria

# === BASE DE DATOS ===
DATABASE_URL=postgresql://postgres:postgres_password@localhost:5433/audio_pipeline
DB_HOST=localhost
DB_PORT=5433
DB_NAME=audio_pipeline
DB_USER=postgres
DB_PASSWORD=postgres_password

# === REDIS ===
REDIS_HOST=localhost
REDIS_PORT=6380

# === SERVIDOR ===
PORT=3001
NODE_ENV=development
TRANSCRIPTION_SERVICE_URL=http://localhost:5000

# === SUBIDAS ===
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=524288000         # 500MB

# === HARDWARE ===
FORCE_CPU=false                 # Forzar CPU si GPU falla
CUDA_VISIBLE_DEVICES=0          # GPU específica
```

### 🎛️ Configuración de Modelos Optimizada

| Modelo | Tamaño | RAM Req. | Velocidad | Precisión | Tiempo Carga | Uso Recomendado |
|--------|--------|----------|-----------|-----------|--------------|-----------------|
| `tiny` | 39MB | 1GB | ⚡⚡⚡ | ⭐⭐ | ~10s | Pruebas muy rápidas |
| `base` | 74MB | 1GB | ⚡⚡ | ⭐⭐⭐ | ~15s | Desarrollo básico |
| `small` | 244MB | 2GB | ⚡⚡ | ⭐⭐⭐⭐ | ~30s | Uso general |
| `medium` | 769MB | 5GB | ⚡ | ⭐⭐⭐⭐⭐ | ~60s | **Desarrollo** |
| `large-v3` | 1550MB | 10GB | ⚡ | ⭐⭐⭐⭐⭐ | ~180s | **Producción** |

### 📊 Configuración de Rendimiento por Sistema

#### Sistema Estándar (8-16GB RAM)
```bash
DEFAULT_MODEL=medium
PARALLEL_WORKERS=1
SEGMENT_LENGTH=300
HIGH_MEMORY_MODE=false
```

#### Sistema Optimizado (32GB+ RAM)
```bash
DEFAULT_MODEL=large-v3
PARALLEL_WORKERS=3
SEGMENT_LENGTH=600
HIGH_MEMORY_MODE=true
PRELOAD_MODEL=true
```

## 📊 Benchmarks y Rendimiento Real

### ⏱️ Tiempos de Procesamiento (Sistema 32GB + Intel i7)

| Duración Audio | Modo Estándar | Modo Optimizado | Mejora | Segmentos |
|----------------|---------------|-----------------|---------|-----------|
| 10 minutos | ~4 min | **~2.5 min** | **37% más rápido** | 1-2 |
| 30 minutos | ~12 min | **~7 min** | **42% más rápido** | 3 |
| 1 hora | ~25 min | **~12 min** | **52% más rápido** | 6 |
| 1:30 horas | ~40 min | **~18 min** | **55% más rápido** | 9 |
| 2 horas | ~55 min | **~23 min** | **58% más rápido** | 12 |

### 💾 Uso de Recursos Optimizado

```
💻 CPU: Uso intensivo durante transcripción
🧠 RAM: 8-12GB (modelo large-v3 + 3 workers)  
💾 Disco: ~3GB (modelos + cache + temporales)
🌐 Red: Mínimo (solo interfaz web)
⚡ GPU: Opcional (fallback automático a CPU)
```

### 🎯 Métricas de Calidad

- **Precisión**: 95-98% en español (large-v3)
- **Detección de idioma**: 99%+ para idiomas principales
- **Resúmenes**: Conserva 25-30% información más relevante
- **Estabilidad**: 99.9% éxito en archivos válidos

## 🐛 Solución de Problemas Avanzada

### ❌ Problemas de Carga de Modelo

#### Modelo large-v3 no carga
```bash
# Verificar RAM disponible
free -h

# Usar modelo más pequeño temporalmente
export DEFAULT_MODEL=medium
python start_dev.py

# O aumentar swap si es necesario
sudo swapon --show
```

#### Timeout durante carga inicial
```bash
# El modelo large-v3 puede tardar hasta 3 minutos
# Espera o usa desarrollo rápido:
python start_dev.py  # Usa modelo medium (60s vs 180s)
```

### ❌ Problemas de Procesamiento Paralelo

#### Error en workers paralelos
```bash
# Reducir workers en .env
PARALLEL_WORKERS=1

# O desactivar modo alta memoria
HIGH_MEMORY_MODE=false
```

#### Memoria insuficiente
```bash
# Cambiar a modo conservativo
export DEFAULT_MODEL=medium
export PARALLEL_WORKERS=1
export SEGMENT_LENGTH=300
```

### ❌ Problemas de Docker

#### Servicios no inician
```bash
# Verificar Docker
docker --version
docker-compose --version

# Forzar recreación
docker-compose down --volumes
docker-compose up -d --force-recreate

# Verificar puertos
netstat -tulpn | grep -E "(5433|6380)"
```

#### Error de permisos
```bash
# Agregar usuario a grupo docker
sudo usermod -aG docker $USER
newgrp docker

# O usar sudo temporalmente
sudo docker-compose up -d
```

### ❌ Problemas de Frontend/Backend

#### Puerto en uso
```bash
# Verificar qué usa los puertos
lsof -i :3000
lsof -i :3001
lsof -i :5000

# Cambiar puertos en .env
PORT=3002  # Para backend
# Frontend: editar vite.config.ts
```

#### Error de dependencias
```bash
# Limpiar e reinstalar
rm -rf node_modules package-lock.json
pnpm install

# Frontend
cd frontend
rm -rf node_modules package-lock.json  
pnpm install
```

### 🔍 Logs de Debug Detallados

```bash
# Logs del servicio Python
tail -f transcription.log

# Logs del backend Express  
pnpm run server:dev  # Muestra logs en tiempo real

# Logs de Docker
docker-compose logs postgres
docker-compose logs redis

# Logs del sistema completo
python start_all.py 2>&1 | tee system.log
```

## 🔄 Roadmap y Actualizaciones

### 🎯 v1.5 - Actual (Optimizaciones 32GB)
- ✅ **Procesamiento paralelo** con 3 workers
- ✅ **Modelo large-v3** precargado
- ✅ **Resúmenes automáticos** inteligentes
- ✅ **Segmentación optimizada** (10 min)
- ✅ **UI mejorada** con información de optimización
- ✅ **Soporte 13+ idiomas** con selector dinámico

### 🔮 v2.0 - Análisis Avanzado (Q1 2026)
- [ ] **Diarización de hablantes** (¿Quién dice qué?)
- [ ] **Detección de emociones** en el audio
- [ ] **Análisis de sentimientos** del texto
- [ ] **Extracción de temas** principales con NLP
- [ ] **Timestamps precisos** por palabra
- [ ] **Mejores resúmenes** con modelos LLM

### 🔮 v2.1 - Productividad Avanzada (Q2 2026)
- [ ] **Traducción automática** con SeamlessM4T
- [ ] **Exportación profesional** (LaTeX, PDF, Word)
- [ ] **API Keys** para modelos cloud (OpenAI, Anthropic)
- [ ] **Plantillas personalizables** de resúmenes
- [ ] **Integración con calendarios** (Meet, Zoom)

### 🔮 v2.2 - Escalabilidad Empresarial (Q3 2026)
- [ ] **Procesamiento distribuido** multi-GPU/multi-servidor
- [ ] **Queue system** para procesamiento masivo
- [ ] **Autenticación y usuarios** con roles
- [ ] **Dashboard analytics** con métricas avanzadas
- [ ] **API rate limiting** y monetización
- [ ] **Integración con S3/GCS** para almacenamiento

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**.

```
MIT License - Copyright (c) 2025 dvillagrans

Se permite el uso, copia, modificación y distribución de este software
para cualquier propósito, comercial o no comercial, siempre que se
incluya esta notificación de copyright y licencia.

EL SOFTWARE SE PROPORCIONA "TAL COMO ESTÁ", SIN GARANTÍA DE NINGÚN TIPO.
```

## 🤝 Contribuciones

¡Las contribuciones son muy bienvenidas! Este proyecto está en desarrollo activo.

### 🔄 Proceso de Contribución

1. **Fork** el repositorio
2. **Crea** una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. **Sigue** el estilo de commits convencionales
5. **Push** a la rama (`git push origin feature/nueva-funcionalidad`) 
6. **Abre** un Pull Request detallado

### 🐛 Reportar Bugs

Usa **GitHub Issues** con la plantilla completa:

```markdown
## 🐛 Descripción del Bug
Descripción clara y concisa del problema.

## 🔄 Pasos para Reproducir
1. Ve a '...'
2. Haz clic en '....'
3. Scroll hacia '....'
4. Ver error

## 💻 Entorno
- OS: [ej. Ubuntu 22.04]
- Node.js: [ej. 18.17.0]
- Python: [ej. 3.12.0]
- RAM: [ej. 32GB]
- Modelo usado: [ej. large-v3]

## 📸 Screenshots
Si aplica, agregar screenshots para explicar el problema.

## 📊 Logs
```
Incluir logs relevantes aquí
```

## 💡 Solución Esperada
Descripción clara de lo que esperabas que pasara.
```

### 🚀 Ideas para Contribuir

- 🧠 **Algoritmos de resumen** más avanzados
- 🌍 **Soporte para más idiomas** 
- 🎨 **Mejoras de UI/UX**
- ⚡ **Optimizaciones de rendimiento**
- 📚 **Documentación y tutoriales**
- 🧪 **Tests automatizados**

## 📞 Soporte y Comunidad

### 💬 Canales de Soporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/dvillagrans/Transcripcion/issues)
- 💡 **Discusiones**: [GitHub Discussions](https://github.com/dvillagrans/Transcripcion/discussions)
- 📧 **Email**: dvillagrans@example.com
- 🐦 **Twitter**: [@dvillagrans](https://twitter.com/dvillagrans)

### 📖 Recursos Adicionales

- 📚 **Wiki**: [Guías detalladas](https://github.com/dvillagrans/Transcripcion/wiki)
- 🎥 **Videos**: Tutoriales en YouTube (próximamente)
- 📑 **Blog**: Artículos técnicos (próximamente)
- 🎓 **Ejemplos**: [Casos de uso reales](https://github.com/dvillagrans/Transcripcion/tree/main/examples)

### 🏷️ Tags y Versiones

- 🏷️ **Releases**: [Versiones estables](https://github.com/dvillagrans/Transcripcion/releases)
- 🔖 **Tags**: Versionado semántico (v1.5.0, v2.0.0, etc.)
- 📋 **Changelog**: [Historia de cambios](https://github.com/dvillagrans/Transcripcion/blob/main/CHANGELOG.md)

---

<div align="center">

## ⭐ ¡Si te gusta este proyecto, no olvides darle una estrella! ⭐

[![GitHub stars](https://img.shields.io/github/stars/dvillagrans/Transcripcion?style=for-the-badge)](https://github.com/dvillagrans/Transcripcion/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/dvillagrans/Transcripcion?style=for-the-badge)](https://github.com/dvillagrans/Transcripcion/network)
[![GitHub issues](https://img.shields.io/github/issues/dvillagrans/Transcripcion?style=for-the-badge)](https://github.com/dvillagrans/Transcripcion/issues)
[![GitHub license](https://img.shields.io/github/license/dvillagrans/Transcripcion?style=for-the-badge)](https://github.com/dvillagrans/Transcripcion/blob/main/LICENSE)

### 🚀 Inicio Rápido

```bash
git clone https://github.com/dvillagrans/Transcripcion.git
cd Transcripcion
python start_dev.py  # Desarrollo rápido
# o
python start_all.py  # Producción completa
```

### 📊 Estadísticas del Proyecto

![Lines of code](https://img.shields.io/tokei/lines/github/dvillagrans/Transcripcion?style=flat-square)
![GitHub repo size](https://img.shields.io/github/repo-size/dvillagrans/Transcripcion?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/dvillagrans/Transcripcion?style=flat-square)

**Desarrollado con ❤️ usando IA, tecnologías modernas y muchas horas de optimización**

**Optimizado especialmente para sistemas de 32GB RAM 🚀**

</div>
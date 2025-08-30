# 🎧 Pipeline de Transcripción de Audio con IA

Pipeline integral de procesamiento de audio que automatiza la transcripción de archivos largos usando tecnologías de inteligencia artificial avanzadas. Diseñado para manejar audios de hasta 1:30 horas con segmentación automática y seguimiento de progreso en tiempo real.

## ✨ Características Principales

### 🚀 Transcripción Avanzada
- **Modelos Whisper Optimizados**: Soporte completo para todos los modelos (tiny, base, small, medium, large-v3)
- **Segmentación Inteligente**: Procesa automáticamente audios largos en segmentos de 5 minutos
- **Múltiples Idiomas**: Español por defecto con selector de 13+ idiomas
- **Progreso en Tiempo Real**: Visualización detallada del progreso por segmento

### 🌍 Soporte Multiidioma
- **Idioma por Defecto**: Español configurado automáticamente
- **Selector Dinámico**: Cambio de idioma en tiempo real
- **Auto-detección**: Opción para detectar idioma automáticamente
- **Idiomas Soportados**: Español, Inglés, Francés, Alemán, Italiano, Portugués, Ruso, Japonés, Coreano, Chino, Árabe, Hindi

### 🎯 Interfaz Moderna
- **UI Intuitiva**: Diseño moderno con animaciones suaves
- **Drag & Drop**: Arrastra archivos directamente
- **Progreso Visual**: Barras de progreso y grids de segmentos
- **Responsive**: Optimizado para desktop y móvil

### ⚡ Rendimiento Optimizado
- **CPU Robusto**: Modo ROBUST_MODE para máxima estabilidad
- **Limpieza Automática**: Los archivos temporales se eliminan automáticamente
- **Timeout Inteligente**: Timeouts dinámicos basados en el tamaño del archivo
- **Gestión de Memoria**: Procesamiento eficiente de archivos grandes

## 🛠️ Stack Tecnológico

### Frontend
- **React 18** + TypeScript
- **Tailwind CSS** + shadcn/ui
- **Vite** para build optimizado
- **Lucide React** para iconografía
- **React Router** para navegación

### Backend
- **Express.js** + TypeScript
- **PostgreSQL** (puerto 5433)
- **Redis** (puerto 6380)
- **Multer** para uploads
- **Axios** para comunicación con servicios

### AI & Processing
- **Faster-Whisper** para transcripción
- **NumPy** para procesamiento de audio
- **Librosa/SoundFile** para manipulación de audio
- **Python 3.12** con virtual environment

### Infrastructure
- **Docker Compose** para servicios
- **Auto-detección** de comandos Docker
- **Scripts automatizados** para setup

## 📋 Requisitos del Sistema

- **Node.js** 18+ y **pnpm**
- **Python** 3.12+ con pip
- **Docker** y **Docker Compose**
- **8GB RAM** mínimo (16GB recomendado)
- **GPU** opcional (CUDA compatible)

## 🚀 Instalación Rápida

### 🎯 Método 1: Setup Automático (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/dvillagrans/Transcripcion.git
cd Transcripcion

# Windows
start_all.bat

# Linux/Mac
python start_all.py
```

### ⚙️ Método 2: Instalación Manual

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

#### 3. Iniciar Servicios
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

| Servicio | URL | Puerto |
|----------|-----|---------|
| **Frontend** | http://localhost:3000 | 3000 |
| **Backend API** | http://localhost:3001 | 3001 |
| **Python Service** | http://localhost:5000 | 5000 |
| **PostgreSQL** | localhost:5433 | 5433 |
| **Redis** | localhost:6380 | 6380 |

## 📁 Estructura del Proyecto

```
Transcripcion/
├── 🎨 frontend/              # React + TypeScript
│   ├── src/
│   │   ├── components/       # Componentes UI
│   │   │   ├── ui/          # shadcn/ui components
│   │   │   ├── LanguageSelector.tsx
│   │   │   ├── SegmentProgressDisplay.tsx
│   │   │   └── Progress.tsx
│   │   ├── pages/           # Páginas principales
│   │   │   ├── HomePage.tsx
│   │   │   ├── ProcessPage.tsx
│   │   │   ├── ConfigPage.tsx
│   │   │   ├── ResultsPage.tsx
│   │   │   └── HistoryPage.tsx
│   │   └── App.tsx
│   └── vite.config.ts
├── 🔧 api/                   # Express.js Backend
│   ├── config/              # DB y Redis
│   ├── models/              # Modelos TypeScript
│   ├── routes/              # API endpoints
│   ├── services/            # Lógica de negocio
│   └── app.ts
├── 🐍 Python Services
│   ├── transcription_service.py  # Servicio principal
│   ├── requirements.txt          # Dependencias Python
│   └── env/                      # Virtual environment
├── 📂 Directorios de Datos
│   ├── uploads/             # Archivos subidos
│   ├── segments/            # Segmentos temporales
│   └── models/              # Modelos Whisper
├── 🐳 Docker
│   ├── docker-compose.yml   # Servicios
│   └── init.sql            # Setup DB
└── 📝 Configuración
    ├── .env                # Variables de entorno
    ├── .gitignore          # Archivos ignorados
    └── README.md           # Este archivo
```

## 🎯 Guía de Uso

### 1. 🎛️ Configuración Inicial
![Config](https://img.shields.io/badge/Paso-1-blue)

- Ve a **Configuración** (`/config`)
- Selecciona el **modelo Whisper** según tus necesidades:
  - `tiny`: Ultra rápido ⚡⚡⚡ (precisión ⭐⭐)
  - `medium`: **Recomendado** ⚡ (precisión ⭐⭐⭐⭐⭐)
  - `large-v3`: Máxima precisión ⚡ (precisión ⭐⭐⭐⭐⭐)
- Configura el **idioma por defecto** (Español preconfigurado)
- Activa/desactiva **resumen automático**

### 2. 🎵 Subir Audio
![Process](https://img.shields.io/badge/Paso-2-green)

- Ve a **Procesar** (`/process`)
- **Arrastra y suelta** o **selecciona archivo**
- Formatos: `MP3`, `WAV`, `FLAC`, `M4A`, `OGG`
- Tamaño máximo: **500MB** (optimizado para audios de 1:30h)
- Selecciona **idioma específico** si es necesario

### 3. 📊 Monitoreo en Tiempo Real
![Progress](https://img.shields.io/badge/Paso-3-orange)

Para **audios largos** (>10 minutos):
- ✅ **Segmentación automática** en bloques de 5 minutos
- 📊 **Grid visual** mostrando cada segmento
- ⏱️ **Tiempo estimado** de finalización
- 🔄 **Progreso por segmento** en tiempo real
- 📈 **Estadísticas técnicas** detalladas

### 4. 📋 Resultados
![Results](https://img.shields.io/badge/Paso-4-purple)

- 📝 **Transcripción completa** y precisa
- 📄 **Resumen automático** (si está activado)
- 💾 **Descarga** en múltiples formatos
- 📋 **Copia rápida** al portapapeles
- 🔍 **Búsqueda** dentro del texto

### 5. 📚 Historial
![History](https://img.shields.io/badge/Paso-5-indigo)

- 📜 **Lista completa** de transcripciones
- 🔍 **Búsqueda rápida** por nombre
- 🗑️ **Eliminación** de trabajos antiguos
- 📊 **Estado** de cada procesamiento

## 🚀 Características Avanzadas

### 🧩 Segmentación Inteligente

```python
# Automático para audios >10 minutos
if audio_duration > 600:  # 10 minutos
    segments = segment_audio(file_path, segment_length=300)  # 5 min c/u
    
# Ejemplo: Audio de 1:30h = 18 segmentos de 5 minutos
```

### 🌍 Soporte Multiidioma

```typescript
const languages = [
  { code: 'es', name: 'Español' },        // Por defecto
  { code: 'en', name: 'English' },
  { code: 'fr', name: 'Français' },
  { code: 'de', name: 'Deutsch' },
  { code: 'auto', name: 'Auto-detectar' }
  // ... 13+ idiomas soportados
];
```

### 📊 Progreso Detallado

```typescript
interface ProgressData {
  segments_total: number;
  segments_completed: number;
  current_segment: number;
  estimated_time_remaining: string;
  processing_speed: string;
  technical_info: TechnicalInfo;
}
```

## 🔧 API Reference

### 🎵 Audio Processing

#### Upload Audio
```bash
POST /api/audio/upload
Content-Type: multipart/form-data

{
  "audioFile": File,
  "whisperModel": "medium",
  "language": "es",
  "generateSummary": true
}
```

#### Get Progress
```bash
GET /api/audio/status/:jobId

Response:
{
  "success": true,
  "data": {
    "jobId": "uuid",
    "status": "processing",
    "progress": 45,
    "currentStage": "Procesando segmento 3/12",
    "segments": {...}
  }
}
```

#### Get Results
```bash
GET /api/audio/results/:jobId

Response:
{
  "success": true,
  "data": {
    "transcription": "Texto completo...",
    "summary": "Resumen automático...",
    "metadata": {
      "duration": "5400s",
      "language": "es",
      "model": "medium"
    }
  }
}
```

### 🐍 Python Service

#### Transcribe Endpoint
```bash
POST http://localhost:5000/transcribe

{
  "file_path": "/path/to/audio.mp3",
  "model": "medium",
  "language": "es",
  "job_id": "uuid"
}
```

#### Progress Endpoint
```bash
GET http://localhost:5000/progress/:jobId

Response:
{
  "progress": 45,
  "stage": "Transcribiendo segmento 3/12",
  "segments_completed": 2,
  "segments_total": 12,
  "estimated_time": "15:30"
}
```

## ⚙️ Configuración Avanzada

### 🔧 Variables de Entorno

```bash
# === DATABASE ===
DB_HOST=localhost
DB_PORT=5433
DB_NAME=audio_pipeline
DB_USER=app_user
DB_PASSWORD=secure_password

# === REDIS ===
REDIS_HOST=localhost
REDIS_PORT=6380

# === SERVER ===
PORT=3001
NODE_ENV=development
TRANSCRIPTION_SERVICE_URL=http://localhost:5000

# === UPLOAD ===
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=524288000  # 500MB

# === AI CONFIG ===
ROBUST_MODE=true
DEFAULT_MODEL=medium
DEFAULT_LANGUAGE=es
```

### 🎛️ Configuración de Modelos

| Modelo | Tamaño | Velocidad | Precisión | RAM | Recomendado Para |
|--------|--------|-----------|-----------|-----|------------------|
| `tiny` | 39MB | ⚡⚡⚡ | ⭐⭐ | 1GB | Pruebas rápidas |
| `base` | 74MB | ⚡⚡ | ⭐⭐⭐ | 1GB | Desarrollo |
| `small` | 244MB | ⚡⚡ | ⭐⭐⭐⭐ | 2GB | Uso general |
| `medium` | 769MB | ⚡ | ⭐⭐⭐⭐⭐ | 5GB | **Recomendado** |
| `large-v3` | 1550MB | ⚡ | ⭐⭐⭐⭐⭐ | 10GB | Máxima calidad |

## 🐛 Solución de Problemas

### ❌ Problemas Comunes

#### Docker no inicia
```bash
# Verificar Docker
docker --version
docker-compose --version

# Reiniciar servicios
docker-compose down
docker-compose up -d --force-recreate
```

#### Error de Python/Whisper
```bash
# Verificar entorno virtual
source env/bin/activate
pip list | grep -E "(torch|whisper|faster)"

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

#### Error de puertos en uso
```bash
# Verificar puertos
netstat -tulpn | grep -E "(3000|3001|5000|5433|6380)"

# Cambiar puertos en .env
PORT=3002
DB_PORT=5434
```

#### Segmentos no se limpian
```bash
# Limpiar manualmente
rm -rf segments/*
```

### 🔍 Logs de Debug

```bash
# Backend logs
cd frontend && pnpm run dev  # Terminal 1
pnpm run server:dev          # Terminal 2

# Python logs
tail -f transcription.log    # Terminal 3

# Docker logs
docker-compose logs postgres
docker-compose logs redis
```

## 📊 Benchmarks y Rendimiento

### ⏱️ Tiempos de Procesamiento (CPU Intel i7)

| Duración Audio | Modelo | Segmentos | Tiempo Procesamiento |
|----------------|--------|-----------|---------------------|
| 5 minutos | medium | 1 | ~2 minutos |
| 30 minutos | medium | 6 | ~10 minutos |
| 1 hora | medium | 12 | ~18 minutos |
| 1:30 horas | medium | 18 | ~25 minutos |

### 💾 Uso de Recursos

- **RAM**: 4-8GB (dependiendo del modelo)
- **CPU**: Uso intensivo durante transcripción
- **Disco**: ~2GB para modelos + archivos temporales
- **Red**: Mínimo (solo para UI)

## 🔄 Roadmap Futuro

### 🎯 Próximas Versiones

#### v2.0 - Análisis Avanzado
- [ ] **Diarización de hablantes** (¿Quién dice qué?)
- [ ] **Detección de emociones** en el audio
- [ ] **Análisis de sentimientos** del texto
- [ ] **Extracción de temas** principales

#### v2.1 - Productividad
- [ ] **Traducción automática** (SeamlessM4T)
- [ ] **Generación de resúmenes** con Llama 3.1
- [ ] **Exportación a LaTeX/PDF** profesional
- [ ] **API Keys** para modelos cloud

#### v2.2 - Escalabilidad
- [ ] **Procesamiento distribuido** multi-GPU
- [ ] **Queue system** para múltiples archivos
- [ ] **Autenticación** y usuarios
- [ ] **Dashboard analytics** avanzado

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**.

```
MIT License - Copyright (c) 2025 dvillagrans

Se permite el uso, copia, modificación y distribución de este software
para cualquier propósito, comercial o no comercial.
```

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! 

### 🔄 Proceso de Contribución

1. **Fork** el repositorio
2. **Crea** una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre** un Pull Request

### 🐛 Reportar Bugs

Usa los **GitHub Issues** con la plantilla:
- 🐛 **Descripción** del problema
- 🔄 **Pasos** para reproducir
- 💻 **Entorno** (OS, Node.js version, etc.)
- 📸 **Screenshots** si aplica

## 📞 Soporte y Contacto

- 💬 **Issues**: [GitHub Issues](https://github.com/dvillagrans/Transcripcion/issues)
- 📧 **Email**: dvillagrans@example.com
- 🐦 **Twitter**: @dvillagrans

---

<div align="center">

**⭐ Si te gusta este proyecto, no olvides darle una estrella ⭐**

[![GitHub stars](https://img.shields.io/github/stars/dvillagrans/Transcripcion)](https://github.com/dvillagrans/Transcripcion/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/dvillagrans/Transcripcion)](https://github.com/dvillagrans/Transcripcion/network)
[![GitHub issues](https://img.shields.io/github/issues/dvillagrans/Transcripcion)](https://github.com/dvillagrans/Transcripcion/issues)

**Desarrollado con ❤️ usando IA y tecnologías modernas**

</div>
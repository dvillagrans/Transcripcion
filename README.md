# Pipeline de Procesamiento de Audio

Pipeline integral de procesamiento de audio que automatiza la transcripción, diarización y postprocesamiento de archivos de audio largos usando tecnologías de inteligencia artificial.

## 🚀 Características

- **Transcripción Automática**: Convierte audio a texto usando modelos Whisper
- **Resúmenes Inteligentes**: Genera resúmenes automáticos del contenido transcrito
- **Interfaz Web Moderna**: Frontend React con diseño responsive
- **API RESTful**: Backend Express.js con endpoints completos
- **Base de Datos**: PostgreSQL con Redis para caching
- **Docker**: Configuración completa con Docker Compose

## 🛠️ Tecnologías

### Frontend
- React 18 + TypeScript
- Tailwind CSS
- Vite
- React Router
- Lucide React (iconos)
- React Dropzone

### Backend
- Express.js + TypeScript
- PostgreSQL (Docker)
- Redis (Docker)
- Multer (upload de archivos)
- Node.js

### AI Services (Futuro)
- Faster-Whisper
- PyAnnote
- SeamlessM4T
- Llama 3.1

## 📋 Requisitos Previos

- Node.js 18+
- Docker y Docker Compose
- pnpm (recomendado) o npm

## 🚀 Instalación y Configuración

### Método 1: Inicio Automático (Recomendado)

#### Windows
```bash
# Ejecutar script de inicio automático
start_all.bat
```

#### Linux/Mac
```bash
# Ejecutar script de inicio automático
python start_all.py
```

### Método 2: Inicio Manual

#### 1. Instalar dependencias
```bash
# Backend
pnpm install

# Frontend
cd frontend
pnpm install
cd ..
```

#### 2. Iniciar servicios Docker
```bash
# Iniciar PostgreSQL y Redis
docker-compose up -d

# Verificar que los servicios estén corriendo
docker-compose ps
```

#### 3. Iniciar servicios de aplicación
```bash
# Terminal 1: Backend (puerto 3001)
pnpm run server:dev

# Terminal 2: Frontend (puerto 3000)
cd frontend
pnpm run dev

# Terminal 3: Servicio Python (puerto 5000)
python transcription_service.py
```

### 🌐 Acceder a la aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **Servicio Python**: http://localhost:5000
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6380

## 📁 Estructura del Proyecto

```
trasncript/
├── api/                    # Backend Express.js
│   ├── config/            # Configuración de DB y Redis
│   ├── models/            # Modelos TypeScript
│   ├── routes/            # Rutas de la API
│   ├── services/          # Lógica de negocio
│   └── app.ts             # Aplicación principal
├── frontend/              # Frontend React
│   ├── src/
│   │   ├── components/    # Componentes reutilizables
│   │   ├── pages/         # Páginas de la aplicación
│   │   └── App.tsx        # Componente principal
│   └── vite.config.ts     # Configuración de Vite
├── uploads/               # Archivos subidos
├── docker-compose.yml     # Servicios Docker
├── init.sql              # Script de inicialización de DB
└── .env                  # Variables de entorno
```

## 🔧 Scripts Disponibles

### Backend
```bash
pnpm run dev          # Desarrollo con nodemon
pnpm run build        # Compilar TypeScript
pnpm run start        # Producción
```

### Frontend
```bash
pnpm run dev          # Servidor de desarrollo
pnpm run build        # Build para producción
pnpm run preview      # Preview del build
```

### Docker
```bash
docker-compose up -d     # Iniciar servicios
docker-compose down      # Detener servicios
docker-compose logs      # Ver logs
```

## 📡 API Endpoints

### Audio Processing
- `POST /api/audio/upload` - Subir y procesar archivo de audio
- `GET /api/audio/status/:jobId` - Obtener estado del procesamiento
- `GET /api/audio/results/:jobId` - Obtener resultados de transcripción
- `GET /api/audio/jobs` - Listar todos los trabajos
- `DELETE /api/audio/jobs/:jobId` - Eliminar trabajo

### Health Check
- `GET /api/health` - Estado del servidor

## 🎯 Uso de la Aplicación

### 1. Configuración
- Accede a `/config` para ajustar parámetros del pipeline
- Selecciona el modelo Whisper (tiny, base, small, medium, large-v3)
- Activa/desactiva la generación de resúmenes

### 2. Procesamiento
- Ve a `/process` para subir archivos de audio
- Arrastra y suelta archivos o haz clic para seleccionar
- Formatos soportados: MP3, WAV, FLAC, M4A, OGG
- Tamaño máximo: 100MB

### 3. Resultados
- Monitorea el progreso en tiempo real
- Accede a `/results/:jobId` para ver transcripciones
- Copia o descarga transcripciones y resúmenes

### 4. Historial
- Ve a `/history` para revisar trabajos anteriores
- Elimina trabajos que ya no necesites
- Accede rápidamente a resultados anteriores

## 🗄️ Base de Datos

### Tabla `jobs`
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'processing',
    transcription TEXT,
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔧 Variables de Entorno

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=audio_pipeline
DB_USER=app_user
DB_PASSWORD=app_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Server
PORT=3001
NODE_ENV=development

# Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100000000
```

## 🚀 Próximas Funcionalidades

- [ ] Integración con Faster-Whisper real
- [ ] Diarización de hablantes con PyAnnote
- [ ] Traducción con SeamlessM4T
- [ ] Generación de resúmenes con Llama 3.1
- [ ] Exportación a formato LaTeX
- [ ] Procesamiento por lotes
- [ ] Autenticación de usuarios

## 🐛 Solución de Problemas

### Error de conexión a la base de datos
```bash
# Verificar que Docker esté corriendo
docker-compose ps

# Reiniciar servicios
docker-compose down
docker-compose up -d
```

### Error de permisos en uploads
```bash
# Crear directorio de uploads
mkdir uploads
chmod 755 uploads
```

### Puerto en uso
```bash
# Cambiar puertos en .env y vite.config.ts
# O detener procesos que usen los puertos 3000/3001
```

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas o preguntas, por favor abre un issue en el repositorio.
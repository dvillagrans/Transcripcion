-- Crear base de datos y usuario de aplicación
CREATE USER app_user WITH PASSWORD 'app_password';
GRANT ALL PRIVILEGES ON DATABASE audio_pipeline TO app_user;

-- Conectar a la base de datos audio_pipeline
\c audio_pipeline;

-- Crear extensión para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear tabla de trabajos
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'error')),
    transcription TEXT,
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_filename ON jobs(filename);

-- Otorgar permisos al usuario de aplicación
GRANT ALL PRIVILEGES ON jobs TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Insertar datos de prueba
INSERT INTO jobs (filename, status, transcription, summary) VALUES 
('ejemplo_audio.mp3', 'completed', 'Esta es una transcripción de ejemplo para probar el sistema.', 'Resumen: Audio de prueba del sistema de transcripción.');

INSERT INTO jobs (filename, status, transcription, summary) VALUES 
('conferencia_test.wav', 'completed', 'Transcripción de una conferencia de ejemplo sobre inteligencia artificial y procesamiento de lenguaje natural.', 'Resumen: Conferencia sobre IA y PLN con conceptos fundamentales.');
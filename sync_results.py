#!/usr/bin/env python3
"""
Sincronización de resultados entre servicio Python y backend Express
Recupera transcripciones completadas que no se guardaron en la base de datos
"""

import requests
import json
import psycopg2
from datetime import datetime
import os
from pathlib import Path

# Configuración
PYTHON_SERVICE_URL = "http://localhost:5000"
EXPRESS_BACKEND_URL = "http://localhost:3001"

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'transcription_db',
    'user': 'transcription_user',
    'password': 'secure_password'
}

def get_incomplete_jobs_from_db():
    """Obtener trabajos que están marcados como en progreso en la BD"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Buscar trabajos en progreso o transcribiendo que no tienen transcripción
        cursor.execute("""
            SELECT id, status, created_at 
            FROM jobs 
            WHERE status IN ('processing', 'transcribiendo') 
               OR (transcription IS NULL AND status != 'failed')
            ORDER BY created_at DESC
        """)
        
        jobs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{'id': job[0], 'status': job[1], 'created_at': job[2]} for job in jobs]
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return []

def check_python_service_status(job_id):
    """Verificar el estado de un trabajo en el servicio Python"""
    try:
        response = requests.get(f"{PYTHON_SERVICE_URL}/progress/{job_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('progress', {})
        return None
    except Exception as e:
        print(f"⚠️ Error verificando estado de {job_id}: {e}")
        return None

def update_job_in_db(job_id, transcription, summary=None):
    """Actualizar trabajo en la base de datos con transcripción y resumen"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        if summary:
            cursor.execute("""
                UPDATE jobs 
                SET transcription = %s, summary = %s, status = 'completed'
                WHERE id = %s
            """, (transcription, summary, job_id))
        else:
            cursor.execute("""
                UPDATE jobs 
                SET transcription = %s, status = 'completed'
                WHERE id = %s
            """, (transcription, job_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error actualizando trabajo {job_id}: {e}")
        return False

def recover_completed_transcriptions():
    """Proceso principal de recuperación"""
    print("🔄 Iniciando sincronización de transcripciones...")
    
    # Obtener trabajos incompletos de la BD
    incomplete_jobs = get_incomplete_jobs_from_db()
    print(f"📋 Trabajos incompletos en BD: {len(incomplete_jobs)}")
    
    recovered = 0
    
    for job in incomplete_jobs:
        job_id = job['id']
        print(f"\n🔍 Verificando trabajo: {job_id}")
        print(f"   Estado actual en BD: {job['status']}")
        
        # Verificar estado en servicio Python
        python_status = check_python_service_status(job_id)
        
        if python_status:
            status = python_status.get('status', 'desconocido')
            progress = python_status.get('progress', 0)
            
            print(f"   Estado en servicio Python: {status} ({progress}%)")
            
            if status == 'completado' and progress == 100:
                print(f"   ✅ Trabajo completado en servicio Python pero no en BD")
                
                # NOTA: El servicio Python no guarda las transcripciones
                # Este script muestra qué trabajos necesitan ser recuperados
                # pero necesitaríamos modificar el servicio Python para guardar resultados
                
                print(f"   ⚠️ Transcripción disponible pero no hay endpoint para recuperarla")
                print(f"   💡 Necesario: modificar servicio Python para guardar resultados")
                
                recovered += 1
            else:
                print(f"   ⏳ Trabajo aún en progreso o no completado")
        else:
            print(f"   ❌ No se pudo verificar estado en servicio Python")
    
    print(f"\n📊 Resumen:")
    print(f"   • Trabajos verificados: {len(incomplete_jobs)}")
    print(f"   • Trabajos completados sin sincronizar: {recovered}")
    
    if recovered > 0:
        print(f"\n💡 Recomendación:")
        print(f"   Los trabajos completados necesitan sincronización manual")
        print(f"   O implementar endpoint de recuperación en servicio Python")

if __name__ == "__main__":
    recover_completed_transcriptions()
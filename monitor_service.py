#!/usr/bin/env python3
"""
Monitorear el estado del servicio de transcripción
"""

import requests
import json
import time
import sys
from datetime import datetime

def check_service_status():
    """Verificar estado del servicio"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servicio funcionando")
            print(f"   • Modelos cargados: {', '.join(data['models_loaded'])}")
            print(f"   • Timestamp: {datetime.fromtimestamp(data['timestamp']).strftime('%H:%M:%S')}")
            return True
        else:
            print(f"❌ Servicio responde con error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servicio no disponible: {e}")
        return False

def check_jobs_progress():
    """Verificar trabajos en progreso"""
    try:
        response = requests.get('http://localhost:5000/progress', timeout=5)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', {})
            
            if not jobs:
                print("📝 No hay trabajos en progreso")
                return
            
            print(f"📊 Trabajos en progreso: {len(jobs)}")
            for job_id, job_data in jobs.items():
                print(f"   • Job {job_id[:8]}...")
                print(f"     - Progreso: {job_data.get('progress', 0)}%")
                print(f"     - Estado: {job_data.get('current_stage', 'Desconocido')}")
                print(f"     - Segmentos: {job_data.get('segments_completed', 0)}/{job_data.get('segments_total', 0)}")
                
                elapsed = job_data.get('elapsed_time', 0)
                remaining = job_data.get('estimated_time_remaining', 'Desconocido')
                print(f"     - Tiempo: {elapsed/60:.1f}min transcurridos, ~{remaining} restantes")
                print()
        else:
            print(f"❌ Error obteniendo progreso: {response.status_code}")
    except Exception as e:
        print(f"❌ Error consultando progreso: {e}")

def monitor_logs():
    """Mostrar últimas líneas del log que indiquen qué modelo se está usando"""
    try:
        with open('transcription.log', 'r') as f:
            lines = f.readlines()
            
        # Buscar las últimas líneas relevantes
        relevant_lines = []
        for line in reversed(lines[-50:]):  # Últimas 50 líneas
            if any(keyword in line for keyword in ['modelo', 'Model', 'large-v3', 'medium', 'Cargando']):
                relevant_lines.insert(0, line.strip())
        
        if relevant_lines:
            print("📋 Últimas actividades de modelos:")
            for line in relevant_lines[-5:]:  # Últimas 5 relevantes
                print(f"   {line}")
        else:
            print("📋 No hay actividad reciente de modelos en logs")
            
    except Exception as e:
        print(f"❌ Error leyendo logs: {e}")

def main():
    """Función principal de monitoreo"""
    print("🔍 MONITOR DEL SERVICIO DE TRANSCRIPCIÓN")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Estado del servicio
    print("1️⃣ ESTADO DEL SERVICIO:")
    service_ok = check_service_status()
    print()
    
    if not service_ok:
        print("❌ Servicio no disponible. Ejecuta: python3 restart_transcription.py")
        return
    
    # 2. Trabajos en progreso
    print("2️⃣ TRABAJOS EN PROGRESO:")
    check_jobs_progress()
    
    # 3. Logs recientes
    print("3️⃣ ACTIVIDAD DE MODELOS:")
    monitor_logs()
    print()
    
    # 4. Recomendaciones
    print("💡 INFORMACIÓN:")
    print("   • Las transcripciones actuales pueden usar 'medium' (iniciadas antes)")
    print("   • Las nuevas transcripciones usarán 'large-v3' (mejor calidad)")
    print("   • Para una nueva transcripción, prueba desde el frontend")
    print("   • Para monitorear en tiempo real: tail -f transcription.log")

if __name__ == "__main__":
    main()
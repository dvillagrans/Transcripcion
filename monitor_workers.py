#!/usr/bin/env python3
"""
Monitor de workers - Herramienta para ver el estado detallado del procesamiento paralelo
"""

import time
import requests
import json
import os
import subprocess
from pathlib import Path

def check_worker_files():
    """Verificar archivos de segmentos y transcripciones temporales"""
    print("🔍 Verificando archivos de trabajo...")
    
    # Buscar archivos de segmentos - están en segments/
    segments_dir = Path("segments")
    
    segment_files = list(segments_dir.glob("*_segment_*.wav"))
    transcription_files = list(segments_dir.glob("transcription_*_segment_*.txt"))
    
    print(f"📂 Archivos de segmentos encontrados: {len(segment_files)}")
    
    # Agrupar por audio original
    segment_groups = {}
    for f in segment_files:
        # Extraer el nombre base del audio
        base_name = f.name.split('_processed_segment_')[0]
        if base_name not in segment_groups:
            segment_groups[base_name] = []
        segment_groups[base_name].append(f)
    
    for base_name, files in segment_groups.items():
        print(f"   📁 {base_name}: {len(files)} segmentos")
    
    print(f"📝 Transcripciones completadas: {len(transcription_files)}")
    
    # Mostrar progreso por audio
    transcription_groups = {}
    for f in transcription_files:
        # Extraer el nombre base del audio
        base_name = f.name.replace('transcription_', '').split('_processed_segment_')[0]
        if base_name not in transcription_groups:
            transcription_groups[base_name] = []
        transcription_groups[base_name].append(f)
    
    for base_name, files in transcription_groups.items():
        print(f"   ✅ {base_name}: {len(files)} transcripciones")
        # Calcular progreso
        total_segments = len(segment_groups.get(base_name, []))
        if total_segments > 0:
            progress = (len(files) / total_segments) * 100
            print(f"      📊 Progreso: {progress:.1f}% ({len(files)}/{total_segments})")
    
    return len(segment_files), len(transcription_files)

def check_process_resources():
    """Verificar recursos del proceso de transcripción"""
    print("\n💻 Estado del proceso de transcripción:")
    
    try:
        # Usar ps para obtener información del proceso
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        
        for line in result.stdout.split('\n'):
            if 'transcription_service.py' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) >= 11:
                    cpu = parts[2]
                    mem = parts[3]
                    print(f"   CPU: {cpu}%")
                    print(f"   RAM: {mem}%")
                    return True
        
        print("   ❌ Proceso no encontrado")
        return False
    except Exception as e:
        print(f"   ❌ Error verificando proceso: {e}")
        return False

def check_service_health():
    """Verificar estado del servicio"""
    print("\n🏥 Estado del servicio:")
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Servicio activo")
            print(f"   📊 Modelos cargados: {data.get('models_loaded', [])}")
        else:
            print(f"   ⚠️ Servicio responde con código: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error conectando al servicio: {e}")

def monitor_continuous():
    """Monitor continuo"""
    print("🔄 Iniciando monitor continuo (Ctrl+C para salir)...")
    
    try:
        while True:
            print("\n" + "="*60)
            print(f"⏰ {time.strftime('%H:%M:%S')}")
            
            segments_total, transcriptions_done = check_worker_files()
            check_process_resources()
            
            if segments_total > 0:
                progress_pct = (transcriptions_done / segments_total) * 100
                print(f"\n📊 Progreso real: {transcriptions_done}/{segments_total} segmentos ({progress_pct:.1f}%)")
                
                if transcriptions_done < segments_total:
                    print(f"⏳ Procesando... quedan {segments_total - transcriptions_done} segmentos")
                else:
                    print("✅ Todos los segmentos completados!")
            
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n👋 Monitor detenido")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        monitor_continuous()
    else:
        print("🎯 Monitor de Workers - Estado Actual")
        print("="*50)
        
        segments_total, transcriptions_done = check_worker_files()
        check_process_resources()
        check_service_health()
        
        if segments_total > 0:
            progress_pct = (transcriptions_done / segments_total) * 100
            print(f"\n📊 Progreso real: {transcriptions_done}/{segments_total} segmentos ({progress_pct:.1f}%)")
        
        print(f"\n💡 Para monitor continuo: python3 {sys.argv[0]} continuous")
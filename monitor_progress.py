#!/usr/bin/env python3
"""
Script para monitorear el progreso de transcripción en tiempo real
"""

import requests
import time
import sys
import json
from datetime import datetime

def monitor_progress(job_id):
    """Monitorear progreso de un trabajo específico"""
    print(f"🎵 Monitoreando progreso del trabajo: {job_id}")
    print("=" * 60)
    
    last_progress = -1
    start_time = time.time()
    
    while True:
        try:
            response = requests.get(f'http://localhost:5000/progress/{job_id}')
            
            if response.status_code == 404:
                print(f"❌ Trabajo {job_id} no encontrado")
                break
            elif response.status_code != 200:
                print(f"❌ Error consultando progreso: {response.status_code}")
                time.sleep(5)
                continue
            
            data = response.json()
            if not data['success']:
                print(f"❌ Error: {data.get('error', 'Error desconocido')}")
                break
            
            progress_info = data['progress']
            current_progress = progress_info['progress']
            
            # Solo imprimir si hay cambios
            if current_progress != last_progress:
                timestamp = datetime.now().strftime("%H:%M:%S")
                status = progress_info['status']
                stage = progress_info['stage']
                
                # Construir línea de progreso
                bar_length = 30
                filled_length = int(bar_length * current_progress // 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                
                # Información adicional
                info_parts = []
                if 'current_segment' in progress_info and progress_info['current_segment'] > 0:
                    info_parts.append(f"Seg: {progress_info['current_segment']}/{progress_info['total_segments']}")
                
                if 'processed_duration' in progress_info and progress_info['processed_duration'] > 0:
                    processed = progress_info['processed_duration']
                    total = progress_info.get('total_duration', 0)
                    info_parts.append(f"Audio: {processed:.1f}s/{total:.1f}s")
                
                if 'estimated_time_remaining' in progress_info and progress_info['estimated_time_remaining']:
                    remaining_min = progress_info['estimated_time_remaining'] / 60
                    info_parts.append(f"Quedan: {remaining_min:.1f}m")
                
                info_str = " | ".join(info_parts)
                if info_str:
                    info_str = f" | {info_str}"
                
                print(f"[{timestamp}] {bar} {current_progress:3d}% | {status} | {stage}{info_str}")
                
                last_progress = current_progress
            
            # Verificar si terminó
            if progress_info['status'] in ['completado', 'error']:
                elapsed = time.time() - start_time
                print("=" * 60)
                if progress_info['status'] == 'completado':
                    print(f"✅ Transcripción completada en {elapsed:.1f} segundos")
                else:
                    print(f"❌ Transcripción falló: {progress_info.get('error', 'Error desconocido')}")
                break
            
            time.sleep(2)  # Actualizar cada 2 segundos
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoreo cancelado por el usuario")
            break
        except requests.exceptions.ConnectionError:
            print("❌ No se puede conectar al servicio de transcripción")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            time.sleep(5)

def list_all_jobs():
    """Listar todos los trabajos en progreso"""
    try:
        response = requests.get('http://localhost:5000/progress')
        
        if response.status_code != 200:
            print(f"❌ Error consultando trabajos: {response.status_code}")
            return
        
        data = response.json()
        if not data['success']:
            print(f"❌ Error: {data.get('error', 'Error desconocido')}")
            return
        
        jobs = data['jobs']
        if not jobs:
            print("📭 No hay trabajos en progreso")
            return
        
        print(f"📋 Trabajos en progreso ({len(jobs)}):")
        print("-" * 80)
        
        for job_id, job_info in jobs.items():
            status = job_info['status']
            progress = job_info['progress']
            stage = job_info['stage']
            elapsed = job_info['elapsed_time']
            
            print(f"🆔 {job_id}")
            print(f"   Status: {status} | Progreso: {progress}% | Tiempo: {elapsed:.1f}s")
            print(f"   Etapa: {stage}")
            print("-" * 80)
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servicio de transcripción")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 monitor_progress.py <job_id>  # Monitorear trabajo específico")
        print("  python3 monitor_progress.py list      # Listar todos los trabajos")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_all_jobs()
    else:
        monitor_progress(command)
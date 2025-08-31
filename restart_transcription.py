#!/usr/bin/env python3
"""
Script para reiniciar el servicio de transcripción con configuración anti-cuDNN crashes
"""

import os
import sys
import time
import subprocess
import signal
import socket
from pathlib import Path

def check_port(port, host='localhost'):
    """Verificar si un puerto está en uso"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0
    except:
        return False

def kill_transcription_processes():
    """Matar todos los procesos de transcripción"""
    try:
        # Buscar procesos de transcripción
        result = subprocess.run(['pgrep', '-f', 'transcription_service.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"🔪 Matando proceso transcripción PID: {pid}")
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(2)
                        # Si sigue vivo, usar SIGKILL
                        try:
                            os.kill(int(pid), 0)  # Verificar si existe
                            os.kill(int(pid), signal.SIGKILL)
                            print(f"🔪 Proceso {pid} forzado a terminar")
                        except ProcessLookupError:
                            pass  # Ya terminó
                    except ProcessLookupError:
                        pass  # Ya no existe
        else:
            print("✅ No hay procesos de transcripción ejecutándose")
            
    except Exception as e:
        print(f"Error matando procesos: {e}")

def set_cuda_environment():
    """Configurar variables de entorno para evitar cuDNN crashes"""
    print("🔧 Configurando entorno CUDA anti-crashes...")
    
    # Desactivar cuDNN completamente
    os.environ['CUDNN_ENABLED'] = 'false'
    os.environ['TORCH_CUDNN_ENABLED'] = 'false'
    
    # Configuración de memoria CUDA
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
    os.environ['CUDA_MEMORY_FRACTION'] = '0.8'
    
    # Forzar uso de implementaciones CUDA nativas en lugar de cuDNN
    os.environ['CUDNN_CONVOLUTION_FWD_ALGO'] = '0'  # IMPLICIT_GEMM
    os.environ['CUDNN_CONVOLUTION_BWD_DATA_ALGO'] = '0'
    os.environ['CUDNN_CONVOLUTION_BWD_FILTER_ALGO'] = '0'
    
    # Configuración robusta
    os.environ['ROBUST_MODE'] = 'true'
    
    print("✅ Variables de entorno CUDA configuradas")

def start_transcription_service():
    """Iniciar el servicio de transcripción con configuración robusta"""
    print("🚀 Iniciando servicio de transcripción...")
    
    # Configurar entorno
    set_cuda_environment()
    
    # Obtener path del Python virtual env
    venv_python = Path(__file__).parent / '.venv' / 'bin' / 'python'
    if not venv_python.exists():
        # Probar con el env folder como fallback
        venv_python = Path(__file__).parent / 'env' / 'bin' / 'python'
        if not venv_python.exists():
            print("❌ No se encontró entorno virtual, usando Python del sistema")
            venv_python = 'python3'
    else:
        print(f"✅ Usando entorno virtual: {venv_python}")
    
    script_path = Path(__file__).parent / 'transcription_service.py'
    
    # Iniciar proceso
    process = subprocess.Popen(
        [str(venv_python), str(script_path)],
        cwd=Path(__file__).parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        env=os.environ.copy()
    )
    
    print(f"🔄 Proceso iniciado con PID: {process.pid}")
    
    # Esperar a que el servicio esté disponible
    print("⏳ Esperando a que el servicio esté disponible...")
    for i in range(60):  # 60 segundos máximo
        if check_port(5000):
            print("✅ Servicio de transcripción disponible en puerto 5000")
            return process
        
        # Verificar si el proceso sigue vivo
        if process.poll() is not None:
            print("❌ El proceso terminó inesperadamente")
            # Mostrar últimas líneas de output
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stdout:
                    print("📄 Últimas líneas de salida:")
                    print(stdout[-1000:])  # Últimos 1000 caracteres
            except:
                pass
            return None
            
        time.sleep(1)
        if i % 10 == 9:
            print(f"⏳ Esperando... ({i+1}/60 segundos)")
    
    print("❌ El servicio no pudo iniciarse en 60 segundos")
    process.terminate()
    return None

def main():
    """Función principal"""
    print("🔄 REINICIANDO SERVICIO DE TRANSCRIPCIÓN")
    print("=" * 50)
    
    # 1. Matar procesos existentes
    print("\n1️⃣ Limpiando procesos existentes...")
    kill_transcription_processes()
    
    # 2. Esperar un poco para que los puertos se liberen
    print("\n2️⃣ Esperando liberación de puertos...")
    time.sleep(3)
    
    # 3. Verificar que el puerto esté libre
    if check_port(5000):
        print("⚠️ Puerto 5000 aún ocupado, esperando más...")
        time.sleep(5)
        if check_port(5000):
            print("❌ Puerto 5000 sigue ocupado. Puede que haya otro proceso.")
            print("   Ejecuta: sudo lsof -i :5000")
            return False
    
    # 4. Iniciar servicio
    print("\n3️⃣ Iniciando servicio con configuración robusta...")
    process = start_transcription_service()
    
    if process:
        print("\n✅ ¡SERVICIO DE TRANSCRIPCIÓN REINICIADO EXITOSAMENTE!")
        print(f"   • PID: {process.pid}")
        print(f"   • URL: http://localhost:5000")
        print(f"   • Configuración: GPU con cuDNN desactivado")
        print("\n💡 Para verificar: curl http://localhost:5000/health")
        return True
    else:
        print("\n❌ Error reiniciando el servicio")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
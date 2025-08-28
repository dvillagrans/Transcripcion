#!/usr/bin/env python3
"""
Script para iniciar todos los servicios del pipeline de audio
Inicia el servicio de transcripción Python y el backend Express
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def run_command(self, command, name, cwd=None):
        """Ejecutar comando en un proceso separado"""
        print(f"🚀 Iniciando {name}...")
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append((process, name))
            
            # Monitor output in a separate thread
            def monitor_output():
                for line in iter(process.stdout.readline, ''):
                    if line.strip():
                        print(f"[{name}] {line.strip()}")
                    if not self.running:
                        break
                        
            thread = threading.Thread(target=monitor_output, daemon=True)
            thread.start()
            
            return process
            
        except Exception as e:
            print(f"❌ Error iniciando {name}: {e}")
            return None
    
    def check_python_service(self):
        """Verificar si el servicio Python está funcionando"""
        try:
            import requests
            response = requests.get('http://localhost:5000/health', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def wait_for_service(self, url, name, timeout=30):
        """Esperar a que un servicio esté disponible"""
        print(f"⏳ Esperando a que {name} esté disponible...")
        
        for i in range(timeout):
            try:
                import requests
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name} está funcionando")
                    return True
            except:
                pass
            
            time.sleep(1)
            
        print(f"❌ {name} no respondió en {timeout} segundos")
        return False
    
    def start_services(self):
        """Iniciar todos los servicios"""
        print("🎵 Iniciando Pipeline de Procesamiento de Audio\n")
        
        # 1. Verificar dependencias
        print("📋 Verificando dependencias...")
        
        # Verificar Python
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            print(f"✅ Python: {result.stdout.strip()}")
        except:
            print("❌ Python no encontrado")
            return False
        
        # Verificar Node.js
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            print(f"✅ Node.js: {result.stdout.strip()}")
        except:
            print("❌ Node.js no encontrado")
            return False
        
        # 2. Verificar y iniciar Docker Compose (base de datos)
        print("\n🐳 Verificando servicios Docker...")
        
        # Verificar si Docker Compose ya está ejecutándose
        try:
            result = subprocess.run(['docker-compose', 'ps'], 
                                  capture_output=True, text=True, cwd=Path(__file__).parent)
            if 'Up' in result.stdout:
                print("✅ Servicios Docker ya están ejecutándose")
            else:
                print("🚀 Iniciando servicios Docker...")
                docker_process = self.run_command(
                    'docker-compose up -d',
                    'Docker Services',
                    cwd=Path(__file__).parent
                )
                if docker_process:
                    time.sleep(8)  # Esperar a que Docker se inicie
                    print("✅ Servicios Docker iniciados")
        except Exception as e:
            print(f"⚠️ Error verificando Docker: {e}")
            print("🚀 Intentando iniciar servicios Docker...")
            docker_process = self.run_command(
                'docker-compose up -d',
                'Docker Services',
                cwd=Path(__file__).parent
            )
            if docker_process:
                time.sleep(8)
                print("✅ Servicios Docker iniciados")
        
        # 3. Iniciar servicio de transcripción Python
        print("\n🐍 Iniciando servicio de transcripción...")
        python_process = self.run_command(
            f'{sys.executable} transcription_service.py',
            'Transcription Service',
            cwd=Path(__file__).parent
        )
        
        if python_process:
            # Esperar a que el servicio Python esté disponible
            if self.wait_for_service('http://localhost:5000/health', 'Servicio de Transcripción'):
                print("✅ Servicio de transcripción funcionando")
            else:
                print("⚠️ Servicio de transcripción no responde, continuando...")
        
        # 4. Iniciar backend Express
        print("\n🚀 Iniciando backend Express...")
        backend_process = self.run_command(
            'pnpm run server:dev',
            'Express Backend',
            cwd=Path(__file__).parent
        )
        
        if backend_process:
            time.sleep(5)
            if self.wait_for_service('http://localhost:3001/api/audio/jobs', 'Backend Express'):
                print("✅ Backend Express funcionando")
            else:
                print("⚠️ Backend Express no responde, pero continuando...")
        
        # 5. Iniciar frontend React
        print("\n⚛️ Iniciando frontend React...")
        frontend_process = self.run_command(
            'pnpm run dev',
            'React Frontend',
            cwd=Path(__file__).parent / 'frontend'
        )
        
        if frontend_process:
            time.sleep(5)
            print("✅ Frontend React iniciado")
        
        # Mostrar resumen
        print("\n🎉 ¡Todos los servicios iniciados!")
        print("\n📋 URLs disponibles:")
        print("   🌐 Frontend:              http://localhost:3000")
        print("   🔧 Backend API:           http://localhost:3001")
        print("   🐍 Servicio Transcripción: http://localhost:5000")
        print("   🐘 PostgreSQL:            localhost:5433")
        print("   🔴 Redis:                 localhost:6380")
        
        print("\n💡 Comandos útiles:")
        print("   - Probar transcripción: curl http://localhost:5000/health")
        print("   - Ver trabajos: curl http://localhost:3001/api/audio/jobs")
        print("   - Parar servicios: Ctrl+C")
        
        return True
    
    def stop_services(self):
        """Parar todos los servicios"""
        print("\n🛑 Parando servicios...")
        self.running = False
        
        for process, name in self.processes:
            try:
                print(f"⏹️ Parando {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"🔪 Forzando cierre de {name}...")
                process.kill()
            except Exception as e:
                print(f"❌ Error parando {name}: {e}")
        
        print("✅ Todos los servicios parados")
    
    def run(self):
        """Ejecutar el gestor de servicios"""
        try:
            if self.start_services():
                print("\n⌨️ Presiona Ctrl+C para parar todos los servicios")
                
                # Mantener el script corriendo
                while self.running:
                    time.sleep(1)
                    
                    # Verificar si algún proceso ha terminado
                    for process, name in self.processes:
                        if process.poll() is not None:
                            print(f"⚠️ {name} se ha detenido inesperadamente")
                            
        except KeyboardInterrupt:
            print("\n🛑 Interrupción recibida...")
        finally:
            self.stop_services()

def main():
    """Función principal"""
    manager = ServiceManager()
    
    # Manejar señales del sistema
    def signal_handler(signum, frame):
        manager.stop_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager.run()

if __name__ == "__main__":
    main()
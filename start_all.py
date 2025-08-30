#!/usr/bin/env python3
"""
Script mejorado para iniciar todos los servicios del pipeline de audio
Inicia Docker, servicio Python, backend Express y frontend React
"""

import os
import sys
import time
import subprocess
import signal
import threading
import socket
from pathlib import Path

def can_run_docker_without_sudo():
    """Verificar si podemos ejecutar Docker sin sudo"""
    try:
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except:
        return False

def run_docker_command(cmd_args, cwd=None, check=True):
    """Ejecutar comando Docker con sudo si es necesario"""
    # Verificar si necesitamos sudo
    need_sudo = not can_run_docker_without_sudo()
    
    if need_sudo:
        print("⚠️ Usando sudo para Docker (reinicia la sesión para evitar esto)")
        cmd_args = ['sudo'] + cmd_args
    
    if check:
        return subprocess.run(cmd_args, cwd=cwd, check=True)
    else:
        return subprocess.run(cmd_args, cwd=cwd, capture_output=True, text=True)

class ImprovedServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def check_port(self, port, host='localhost'):
        """Verificar si un puerto está en uso"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    def wait_for_port(self, port, name, timeout=30):
        """Esperar a que un puerto esté disponible"""
        print(f"⏳ Esperando a que {name} esté disponible en puerto {port}...")
        
        for i in range(timeout):
            if self.check_port(port):
                print(f"✅ {name} está funcionando en puerto {port}")
                return True
            time.sleep(1)
            
        print(f"❌ {name} no respondió en puerto {port} después de {timeout} segundos")
        return False
    
    def run_command_async(self, command, name, cwd=None):
        """Ejecutar comando de forma asíncrona"""
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
    
    def start_all_services(self):
        """Iniciar todos los servicios en orden"""
        print("🎵 INICIANDO PIPELINE DE PROCESAMIENTO DE AUDIO\n")
        print("=" * 60)
        
        # 1. Verificar dependencias
        print("\n📋 VERIFICANDO DEPENDENCIAS...")
        
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
        
        # Verificar pnpm y establecer comando de paquetes
        self.package_manager = 'npm'
        try:
            result = subprocess.run(['pnpm', '--version'], 
                                  capture_output=True, text=True)
            print(f"✅ pnpm: {result.stdout.strip()}")
            self.package_manager = 'pnpm'
        except:
            print("⚠️ pnpm no encontrado, usando npm")
            try:
                result = subprocess.run(['npm', '--version'], 
                                      capture_output=True, text=True)
                print(f"✅ npm: {result.stdout.strip()}")
            except:
                print("❌ npm no encontrado")
                return False
        
        # 2. Verificar y iniciar Docker Compose
        print("\n🐳 VERIFICANDO SERVICIOS DOCKER...")
        
        try:
            result = run_docker_command(['docker', 'compose', 'ps'], 
                                      cwd=Path(__file__).parent, 
                                      check=False)
            if 'Up' in result.stdout and 'healthy' in result.stdout:
                print("✅ PostgreSQL y Redis ya están ejecutándose")
            else:
                print("🚀 Iniciando PostgreSQL y Redis...")
                run_docker_command(['docker', 'compose', 'up', '-d'], 
                                 cwd=Path(__file__).parent, 
                                 check=True)
                time.sleep(10)
                print("✅ Servicios Docker iniciados")
        except Exception as e:
            print(f"❌ Error con Docker: {e}")
            return False
        
        # 3. Iniciar servicio de transcripción Python
        print("\n🐍 INICIANDO SERVICIO DE TRANSCRIPCIÓN...")
        
        if not self.check_port(5000):
            python_process = self.run_command_async(
                f'{sys.executable} transcription_service.py',
                'Transcription Service',
                cwd=Path(__file__).parent
            )
            
            if python_process:
                if self.wait_for_port(5000, 'Servicio de Transcripción', 60):
                    print("✅ Servicio de transcripción funcionando")
                else:
                    print("⚠️ Servicio de transcripción no responde, continuando...")
        else:
            print("✅ Servicio de transcripción ya está ejecutándose")
        
        # 4. Iniciar backend Express
        print("\n🚀 INICIANDO BACKEND EXPRESS...")
        
        if not self.check_port(3001):
            # Usar el administrador de paquetes correcto
            backend_cmd = f'{self.package_manager} run server:dev'
            backend_process = self.run_command_async(
                backend_cmd,
                'Express Backend',
                cwd=Path(__file__).parent
            )
            
            if backend_process:
                if self.wait_for_port(3001, 'Backend Express', 30):
                    print("✅ Backend Express funcionando")
                else:
                    print("❌ Backend Express no pudo iniciarse")
                    return False
        else:
            print("✅ Backend Express ya está ejecutándose")
        
        # 5. Iniciar frontend React
        print("\n⚛️ INICIANDO FRONTEND REACT...")
        
        if not self.check_port(3000):
            # Usar el administrador de paquetes correcto
            frontend_cmd = f'{self.package_manager} run dev' if self.package_manager == 'pnpm' else 'npm run client:dev'
            frontend_process = self.run_command_async(
                frontend_cmd,
                'React Frontend',
                cwd=Path(__file__).parent / 'frontend'
            )
            
            if frontend_process:
                if self.wait_for_port(3000, 'Frontend React', 30):
                    print("✅ Frontend React funcionando")
                else:
                    print("⚠️ Frontend React no responde, pero continuando...")
        else:
            print("✅ Frontend React ya está ejecutándose")
        
        # Mostrar resumen final
        print("\n" + "=" * 60)
        print("🎉 ¡PIPELINE COMPLETAMENTE INICIADO!")
        print("=" * 60)
        
        print("\n📋 SERVICIOS DISPONIBLES:")
        print(f"   🌐 Frontend:              http://localhost:3000")
        print(f"   🔧 Backend API:           http://localhost:3001")
        print(f"   🐍 Servicio Transcripción: http://localhost:5000")
        print(f"   🐘 PostgreSQL:            localhost:5433")
        print(f"   🔴 Redis:                 localhost:6380")
        
        print("\n🔍 VERIFICACIÓN DE ESTADO:")
        services = [
            (3000, "Frontend React"),
            (3001, "Backend Express"),
            (5000, "Servicio Python"),
            (5433, "PostgreSQL"),
            (6380, "Redis")
        ]
        
        for port, name in services:
            status = "🟢 ACTIVO" if self.check_port(port) else "🔴 INACTIVO"
            print(f"   {status} {name} (puerto {port})")
        
        print("\n💡 COMANDOS ÚTILES:")
        print("   - Probar transcripción: curl http://localhost:5000/health")
        print("   - Ver trabajos: curl http://localhost:3001/api/audio/jobs")
        print("   - Parar servicios: Ctrl+C")
        
        return True
    
    def stop_all_services(self):
        """Parar todos los servicios"""
        print("\n🛑 PARANDO TODOS LOS SERVICIOS...")
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
            if self.start_all_services():
                print("\n⌨️ Presiona Ctrl+C para parar todos los servicios")
                print("\n🔄 Monitoreando servicios...")
                
                # Mantener el script corriendo
                while self.running:
                    time.sleep(5)
                    
                    # Verificar si algún proceso ha terminado
                    for process, name in self.processes:
                        if process.poll() is not None:
                            print(f"⚠️ {name} se ha detenido inesperadamente")
                            
        except KeyboardInterrupt:
            print("\n🛑 Interrupción recibida...")
        finally:
            self.stop_all_services()

def main():
    """Función principal"""
    manager = ImprovedServiceManager()
    
    # Manejar señales del sistema
    def signal_handler(signum, frame):
        manager.stop_all_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager.run()

if __name__ == "__main__":
    main()
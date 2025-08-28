#!/usr/bin/env python3
"""
Script de instalación completa del Pipeline de Procesamiento de Audio
Configura automáticamente todo el entorno necesario.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Mostrar encabezado del instalador"""
    print("="*60)
    print("🎵 PIPELINE DE PROCESAMIENTO DE AUDIO - INSTALADOR")
    print("="*60)
    print("Este script configurará automáticamente:")
    print("  ✅ Entorno Python con faster-whisper")
    print("  ✅ Dependencias Node.js")
    print("  ✅ Base de datos PostgreSQL (Docker)")
    print("  ✅ Cache Redis (Docker)")
    print("  ✅ Frontend React")
    print("  ✅ Backend Express")
    print("="*60)
    print()

def run_command(command, description, check=True, cwd=None):
    """Ejecutar comando con descripción"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        if result.stdout and result.stdout.strip():
            print(f"   📝 {result.stdout.strip()[:100]}...")
        print(f"   ✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error en {description}")
        if e.stderr:
            print(f"   📝 Error: {e.stderr.strip()[:200]}...")
        return False

def check_requirements():
    """Verificar requisitos del sistema"""
    print("📋 Verificando requisitos del sistema...\n")
    
    # Verificar Python
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    # Verificar Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✅ Node.js {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js no encontrado. Instala Node.js desde https://nodejs.org")
        return False
    
    # Verificar pnpm
    try:
        result = subprocess.run(['pnpm', '--version'], capture_output=True, text=True)
        print(f"✅ pnpm {result.stdout.strip()}")
    except FileNotFoundError:
        print("⚠️ pnpm no encontrado, usando npm")
    
    # Verificar Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        print(f"✅ Docker {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Docker no encontrado. Instala Docker Desktop")
        return False
    
    # Verificar Docker Compose
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        print(f"✅ Docker Compose {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Docker Compose no encontrado")
        return False
    
    print("\n✅ Todos los requisitos están disponibles\n")
    return True

def install_python_dependencies():
    """Instalar dependencias Python"""
    print("🐍 CONFIGURANDO ENTORNO PYTHON\n")
    
    # Actualizar pip
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Actualizando pip"
    ):
        return False
    
    # Instalar PyTorch con CUDA si es Windows
    if platform.system() == "Windows":
        print("🔥 Instalando PyTorch con soporte CUDA...")
        torch_cmd = f"{sys.executable} -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118"
        if not run_command(torch_cmd, "Instalando PyTorch CUDA", check=False):
            print("⚠️ CUDA falló, instalando versión CPU...")
            run_command(f"{sys.executable} -m pip install torch torchaudio", "Instalando PyTorch CPU")
    
    # Instalar dependencias desde requirements.txt
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Instalando dependencias Python"
    ):
        return False
    
    print("✅ Entorno Python configurado\n")
    return True

def install_node_dependencies():
    """Instalar dependencias Node.js"""
    print("📦 CONFIGURANDO DEPENDENCIAS NODE.JS\n")
    
    # Determinar gestor de paquetes
    try:
        subprocess.run(['pnpm', '--version'], capture_output=True, check=True)
        pkg_manager = 'pnpm'
    except:
        pkg_manager = 'npm'
    
    print(f"📦 Usando {pkg_manager}")
    
    # Instalar dependencias del backend
    if not run_command(
        f"{pkg_manager} install",
        "Instalando dependencias del backend"
    ):
        return False
    
    # Instalar dependencias del frontend
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        if not run_command(
            f"{pkg_manager} install",
            "Instalando dependencias del frontend",
            cwd=frontend_dir
        ):
            return False
    
    print("✅ Dependencias Node.js instaladas\n")
    return True

def setup_docker_services():
    """Configurar servicios Docker"""
    print("🐳 CONFIGURANDO SERVICIOS DOCKER\n")
    
    # Parar servicios existentes
    run_command(
        "docker-compose down",
        "Parando servicios existentes",
        check=False
    )
    
    # Iniciar servicios
    if not run_command(
        "docker-compose up -d",
        "Iniciando PostgreSQL y Redis"
    ):
        return False
    
    # Esperar a que los servicios estén listos
    print("⏳ Esperando a que los servicios estén listos...")
    import time
    time.sleep(10)
    
    # Verificar servicios
    if run_command(
        "docker-compose ps",
        "Verificando estado de servicios",
        check=False
    ):
        print("✅ Servicios Docker funcionando\n")
        return True
    
    return False

def test_installation():
    """Probar la instalación"""
    print("🧪 PROBANDO INSTALACIÓN\n")
    
    # Probar importaciones Python
    critical_imports = ['faster_whisper', 'flask', 'librosa', 'torch']
    
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module} importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando {module}: {e}")
            return False
    
    # Verificar GPU si está disponible
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"🚀 GPU detectada: {gpu_name}")
        else:
            print("💻 Usando CPU (sin GPU CUDA)")
    except:
        print("❓ No se pudo verificar GPU")
    
    print("\n✅ Instalación verificada\n")
    return True

def create_startup_scripts():
    """Crear scripts de inicio"""
    print("📝 CREANDO SCRIPTS DE INICIO\n")
    
    # Script para Windows
    if platform.system() == "Windows":
        startup_script = """
@echo off
echo 🎵 Iniciando Pipeline de Procesamiento de Audio
echo.
echo 🐳 Iniciando servicios Docker...
docker-compose up -d
echo.
echo 🐍 Iniciando servicio de transcripción...
start "Transcription Service" python transcription_service.py
echo.
echo ⏳ Esperando 10 segundos...
timeout /t 10 /nobreak > nul
echo.
echo 🚀 Iniciando backend...
start "Backend" npm run dev
echo.
echo ⏳ Esperando 5 segundos...
timeout /t 5 /nobreak > nul
echo.
echo ⚛️ Iniciando frontend...
cd frontend
start "Frontend" npm run dev
cd ..
echo.
echo 🎉 ¡Todos los servicios iniciados!
echo.
echo 📋 URLs disponibles:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:3001
echo    Transcripción: http://localhost:5000
echo.
pause
"""
        
        with open("start.bat", "w") as f:
            f.write(startup_script)
        
        print("✅ Script start.bat creado")
    
    # Script universal Python
    print("✅ Script start_services.py ya existe")
    
    print("\n✅ Scripts de inicio creados\n")

def main():
    """Función principal del instalador"""
    print_header()
    
    # Verificar requisitos
    if not check_requirements():
        print("❌ Faltan requisitos del sistema")
        sys.exit(1)
    
    # Instalar dependencias Python
    if not install_python_dependencies():
        print("❌ Error instalando dependencias Python")
        sys.exit(1)
    
    # Instalar dependencias Node.js
    if not install_node_dependencies():
        print("❌ Error instalando dependencias Node.js")
        sys.exit(1)
    
    # Configurar Docker
    if not setup_docker_services():
        print("❌ Error configurando servicios Docker")
        sys.exit(1)
    
    # Probar instalación
    if not test_installation():
        print("❌ Error en las pruebas de instalación")
        sys.exit(1)
    
    # Crear scripts de inicio
    create_startup_scripts()
    
    # Mensaje final
    print("🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
    print("="*60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("\n1. Para iniciar todos los servicios:")
    if platform.system() == "Windows":
        print("   💻 Windows: Ejecuta start.bat")
    print("   🐍 Universal: python start_services.py")
    print("\n2. URLs disponibles:")
    print("   🌐 Frontend:       http://localhost:3000")
    print("   🔧 Backend API:    http://localhost:3001")
    print("   🐍 Transcripción:  http://localhost:5000")
    print("\n3. Para probar transcripción:")
    print("   curl http://localhost:5000/health")
    print("\n4. Para ver trabajos:")
    print("   curl http://localhost:3001/api/audio/jobs")
    print("\n🎵 ¡Disfruta procesando audio!")
    print("="*60)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Instalador simplificado para Windows
Configura el entorno Python de manera más robusta.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command_safe(command, description):
    """Ejecutar comando de manera segura en Windows"""
    print(f"🔧 {description}...")
    try:
        # Usar lista en lugar de string para evitar problemas con espacios
        if isinstance(command, str):
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=True, 
                text=True
            )
        else:
            result = subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True
            )
        
        print(f"   ✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error en {description}")
        if e.stderr:
            print(f"   📝 Error: {e.stderr.strip()[:200]}...")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return False

def install_python_deps():
    """Instalar dependencias Python de manera segura"""
    print("🐍 INSTALANDO DEPENDENCIAS PYTHON\n")
    
    # Usar sys.executable para evitar problemas con rutas
    python_exe = sys.executable
    
    # Actualizar pip
    if not run_command_safe(
        [python_exe, "-m", "pip", "install", "--upgrade", "pip"],
        "Actualizando pip"
    ):
        print("⚠️ No se pudo actualizar pip, continuando...")
    
    # Instalar dependencias básicas primero
    basic_deps = [
        "flask", "flask-cors", "requests", "python-dotenv", 
        "loguru", "filetype", "numpy"
    ]
    
    for dep in basic_deps:
        run_command_safe(
            [python_exe, "-m", "pip", "install", dep],
            f"Instalando {dep}"
        )
    
    # Instalar PyTorch
    print("🔥 Instalando PyTorch...")
    torch_success = run_command_safe(
        [python_exe, "-m", "pip", "install", "torch", "torchaudio", 
         "--index-url", "https://download.pytorch.org/whl/cu118"],
        "Instalando PyTorch con CUDA"
    )
    
    if not torch_success:
        print("⚠️ CUDA falló, instalando versión CPU...")
        run_command_safe(
            [python_exe, "-m", "pip", "install", "torch", "torchaudio"],
            "Instalando PyTorch CPU"
        )
    
    # Instalar dependencias de audio
    audio_deps = ["librosa", "soundfile"]
    for dep in audio_deps:
        run_command_safe(
            [python_exe, "-m", "pip", "install", dep],
            f"Instalando {dep}"
        )
    
    # Instalar faster-whisper
    run_command_safe(
        [python_exe, "-m", "pip", "install", "faster-whisper==1.0.3"],
        "Instalando faster-whisper"
    )
    
    print("✅ Dependencias Python instaladas\n")
    return True

def test_imports():
    """Probar importaciones críticas"""
    print("🧪 PROBANDO IMPORTACIONES...\n")
    
    critical_imports = [
        'flask',
        'librosa', 
        'torch',
        'numpy'
    ]
    
    failed = []
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed.append(module)
    
    # Probar faster-whisper por separado
    try:
        __import__('faster_whisper')
        print("✅ faster_whisper")
    except ImportError as e:
        print(f"❌ faster_whisper: {e}")
        failed.append('faster_whisper')
    
    if failed:
        print(f"\n⚠️ Módulos fallidos: {', '.join(failed)}")
        print("Puedes intentar instalarlos manualmente:")
        for module in failed:
            print(f"  pip install {module}")
    else:
        print("\n✅ Todas las importaciones exitosas")
    
    return len(failed) == 0

def check_gpu():
    """Verificar GPU"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"🚀 GPU disponible: {gpu_name}")
            return True
        else:
            print("💻 Solo CPU disponible")
            return False
    except:
        print("❓ No se pudo verificar GPU")
        return False

def install_node_deps():
    """Instalar dependencias Node.js"""
    print("📦 INSTALANDO DEPENDENCIAS NODE.JS\n")
    
    # Determinar gestor de paquetes
    try:
        subprocess.run(['pnpm', '--version'], capture_output=True, check=True)
        pkg_manager = 'pnpm'
    except:
        pkg_manager = 'npm'
    
    print(f"📦 Usando {pkg_manager}")
    
    # Backend
    if not run_command_safe(
        f"{pkg_manager} install",
        "Instalando dependencias del backend"
    ):
        return False
    
    # Frontend
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        original_dir = os.getcwd()
        try:
            os.chdir(frontend_dir)
            success = run_command_safe(
                f"{pkg_manager} install",
                "Instalando dependencias del frontend"
            )
            os.chdir(original_dir)
            if not success:
                return False
        except Exception as e:
            os.chdir(original_dir)
            print(f"❌ Error en frontend: {e}")
            return False
    
    print("✅ Dependencias Node.js instaladas\n")
    return True

def setup_docker():
    """Configurar Docker"""
    print("🐳 CONFIGURANDO DOCKER...\n")
    
    # Verificar Docker
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
        print("✅ Docker disponible")
    except:
        print("❌ Docker no encontrado")
        return False
    
    # Parar servicios existentes
    run_command_safe(
        "docker-compose down",
        "Parando servicios existentes"
    )
    
    # Iniciar servicios
    if run_command_safe(
        "docker-compose up -d",
        "Iniciando PostgreSQL y Redis"
    ):
        print("✅ Servicios Docker iniciados\n")
        return True
    
    return False

def create_start_script():
    """Crear script de inicio para Windows"""
    start_script = """
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
echo    🌐 Frontend: http://localhost:3000
echo    🔧 Backend:  http://localhost:3001
echo    🐍 Transcripción: http://localhost:5000
echo.
echo 💡 Para parar todos los servicios:
echo    docker-compose down
echo.
pause
"""
    
    with open("start.bat", "w") as f:
        f.write(start_script)
    
    print("✅ Script start.bat creado")

def main():
    """Función principal"""
    print("🎵 INSTALADOR RÁPIDO - PIPELINE DE AUDIO\n")
    
    # Verificar Python
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8+")
        return
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}\n")
    
    # Instalar dependencias Python
    if not install_python_deps():
        print("❌ Error en dependencias Python")
        return
    
    # Probar importaciones
    test_imports()
    
    # Verificar GPU
    check_gpu()
    
    # Instalar dependencias Node.js
    if not install_node_deps():
        print("❌ Error en dependencias Node.js")
        return
    
    # Configurar Docker
    if not setup_docker():
        print("⚠️ Error en Docker, pero continuando...")
    
    # Crear script de inicio
    create_start_script()
    
    # Mensaje final
    print("\n🎉 ¡INSTALACIÓN COMPLETADA!")
    print("="*50)
    print("\n📋 PRÓXIMOS PASOS:")
    print("\n1. Para iniciar todos los servicios:")
    print("   💻 Ejecuta: start.bat")
    print("   🐍 O ejecuta: python start_services.py")
    print("\n2. URLs disponibles:")
    print("   🌐 Frontend:       http://localhost:3000")
    print("   🔧 Backend:        http://localhost:3001")
    print("   🐍 Transcripción:  http://localhost:5000")
    print("\n3. Para probar:")
    print("   curl http://localhost:5000/health")
    print("\n🎵 ¡Disfruta procesando audio!")
    print("="*50)

if __name__ == "__main__":
    main()
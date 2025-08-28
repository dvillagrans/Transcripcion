#!/usr/bin/env python3
"""
Script de instalación automática para el servicio de transcripción
Configura el entorno Python y las dependencias necesarias.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, check=True):
    """Ejecutar comando del sistema"""
    print(f"Ejecutando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python():
    """Verificar versión de Python"""
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    
    print("✅ Versión de Python compatible")
    return True

def check_pip():
    """Verificar que pip esté disponible"""
    try:
        import pip
        print("✅ pip disponible")
        return True
    except ImportError:
        print("❌ pip no encontrado")
        return False

def install_requirements():
    """Instalar dependencias desde requirements.txt"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ Archivo requirements.txt no encontrado")
        return False
    
    print("📦 Instalando dependencias...")
    
    # Actualizar pip primero
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    
    # Instalar PyTorch con CUDA si está disponible
    if platform.system() == "Windows":
        print("🔥 Instalando PyTorch con soporte CUDA...")
        torch_command = f"{sys.executable} -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118"
        if not run_command(torch_command, check=False):
            print("⚠️ Instalación CUDA falló, instalando versión CPU...")
            run_command(f"{sys.executable} -m pip install torch torchaudio")
    
    # Instalar resto de dependencias
    success = run_command(f"{sys.executable} -m pip install -r {requirements_file}")
    
    if success:
        print("✅ Dependencias instaladas correctamente")
    else:
        print("❌ Error instalando dependencias")
    
    return success

def test_imports():
    """Probar importaciones críticas"""
    print("🧪 Probando importaciones...")
    
    critical_imports = [
        'faster_whisper',
        'flask',
        'librosa',
        'soundfile',
        'torch',
        'numpy'
    ]
    
    failed_imports = []
    
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Falló la importación de: {', '.join(failed_imports)}")
        return False
    
    print("\n✅ Todas las importaciones exitosas")
    return True

def check_gpu():
    """Verificar disponibilidad de GPU"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"🚀 GPU disponible: {gpu_name} ({gpu_count} dispositivos)")
            return True
        else:
            print("💻 Solo CPU disponible (sin GPU CUDA)")
            return False
    except ImportError:
        print("❓ No se pudo verificar GPU (PyTorch no instalado)")
        return False

def create_env_file():
    """Crear archivo .env con configuración por defecto"""
    env_file = Path(__file__).parent / ".env.transcription"
    
    if env_file.exists():
        print("✅ Archivo .env.transcription ya existe")
        return
    
    env_content = """# Configuración del servicio de transcripción
TRANSCRIPTION_PORT=5000
WHISPER_MODEL=medium
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE=float16
MAX_FILE_SIZE=500
LOG_LEVEL=INFO
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Archivo .env.transcription creado")

def main():
    """Función principal de instalación"""
    print("🎵 Configurando servicio de transcripción de audio\n")
    
    # Verificaciones básicas
    if not check_python():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Instalación
    if not install_requirements():
        print("\n❌ Error en la instalación")
        sys.exit(1)
    
    # Pruebas
    if not test_imports():
        print("\n❌ Error en las importaciones")
        sys.exit(1)
    
    # Verificaciones adicionales
    check_gpu()
    create_env_file()
    
    print("\n🎉 ¡Instalación completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Ejecutar: python transcription_service.py")
    print("2. El servicio estará disponible en http://localhost:5000")
    print("3. Probar con: curl http://localhost:5000/health")
    
if __name__ == "__main__":
    main()
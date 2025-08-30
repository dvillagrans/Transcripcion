#!/usr/bin/env python3
"""
Script de desarrollo rápido - usa modelo medium para carga más rápida
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    print("🚧 MODO DESARROLLO - Carga Rápida")
    print("📝 Usando modelo 'medium' en lugar de 'large-v3' para desarrollo")
    
    # Configurar variables de entorno para modo desarrollo
    env = os.environ.copy()
    env['DEV_MODE'] = 'true'
    env['DEFAULT_MODEL'] = 'medium'
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Ejecutar start_all.py con variables de desarrollo
    try:
        subprocess.run([sys.executable, 'start_all.py'], env=env, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando start_all.py: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
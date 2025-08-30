#!/usr/bin/env python3
"""
Helper para ejecutar comandos Docker con o sin sudo según sea necesario
"""

import subprocess
import os
import sys

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
        print("⚠️ Ejecutando Docker con sudo (necesario hasta reiniciar sesión)")
        cmd_args = ['sudo'] + cmd_args
    
    if check:
        return subprocess.run(cmd_args, cwd=cwd, check=True)
    else:
        return subprocess.run(cmd_args, cwd=cwd, capture_output=True, text=True)

def main():
    """Función de prueba"""
    print("🔍 Verificando permisos de Docker...")
    
    if can_run_docker_without_sudo():
        print("✅ Docker funciona sin sudo")
    else:
        print("⚠️ Docker requiere sudo (reinicia la sesión para evitar esto)")
    
    # Prueba básica
    try:
        result = run_docker_command(['docker', '--version'], check=False)
        print(f"Docker version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

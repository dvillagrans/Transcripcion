@echo off
echo ============================================================
echo 🎵 PIPELINE DE PROCESAMIENTO DE AUDIO - INICIO RAPIDO
echo ============================================================
echo.
echo Iniciando todos los servicios del pipeline...
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor instala Python.
    pause
    exit /b 1
)

REM Verificar si Node.js está disponible
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js no encontrado. Por favor instala Node.js.
    pause
    exit /b 1
)

REM Verificar si Docker está disponible
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no encontrado. Por favor instala Docker.
    pause
    exit /b 1
)

echo ✅ Todas las dependencias están disponibles
echo.

REM Ejecutar el script Python mejorado
echo 🚀 Ejecutando script de inicio...
echo.
python start_all.py

echo.
echo ✅ Script finalizado.
pause
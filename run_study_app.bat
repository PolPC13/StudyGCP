@echo off
REM Script para lanzar la app de estudio GCP

cd /d "%~dp0"

REM Verificar si existe el virtual environment
if not exist ".venv" (
    echo Creando virtual environment...
    python -m venv .venv
)

REM Activar el virtual environment
call .venv\Scripts\activate.bat

REM Instalar dependencias si es necesario
pip install flask -q

REM Iniciar la app
echo.
echo ================================================
echo  GCP Study App - Localhost
echo ================================================
echo.
echo  Abriendo en: http://localhost:5000
echo  Presiona CTRL+C para detener el servidor
echo.
echo ================================================
echo.

start http://localhost:5000
python app.py

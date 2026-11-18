@echo off
rem Doble clic para abrir el menu de pruebas de carga en la nube.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\pruebas.ps1"
pause

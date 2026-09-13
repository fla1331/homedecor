@echo off
start cmd /k "cd docs && live-server"
start cmd /k "python gerador.py"
echo ✅ Ambientes iniciados!
pause  
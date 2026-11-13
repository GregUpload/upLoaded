@echo off
setlocal
where py >nul 2>nul
if errorlevel 1 (
  echo [ERREUR] Le launcher de Python Windows (py) est introuvable.
  echo Installe Python sur la machine de preparation ou utilise prepare_payload.py avec python.
  exit /b 1
)
py -3 prepare_payload.py
if errorlevel 1 exit /b 1
echo [OK] payload.zip prepare.
endlocal

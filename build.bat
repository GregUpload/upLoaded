@echo off
setlocal
where gcc >nul 2>nul || (echo [ERREUR] gcc introuvable. Ajoute MinGW-w64 au PATH.& exit /b 1)
where windres >nul 2>nul || (echo [ERREUR] windres introuvable. Ajoute MinGW-w64 au PATH.& exit /b 1)
if not exist payload.zip (
  echo [ERREUR] payload.zip absent. Lance d'abord prepare_payload.bat
  exit /b 1
)
windres resources.rc -O coff -o resources.o
if errorlevel 1 exit /b 1
gcc launcher.c resources.o -o Application.exe -municode -mwindows -O2 -Wall -Wextra -lshell32
if errorlevel 1 exit /b 1
echo.
echo [OK] Application.exe genere.
endlocal

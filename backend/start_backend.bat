@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Backend Server Launcher
color 0a
cls

cd /d %~dp0

echo.
echo.
echo  ================================================
echo.
echo.
echo  SITE GUARDIAN BACKEND SERVER
echo  Developed By Serkan Gürcan
echo.
echo  ================================================
echo.

echo   [*] Calisma dizini: %~dp0
echo   [*] Python kontrol ediliyor...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   [!] ERROR: Python bulunamadi
    echo.
    echo   Cozum: PATH'e Python ekleyin veya yeniden kurun
    echo.
    pause
    exit /b 1
)

python --version

echo.
echo  ================================================
echo   [OK] Tum kontroller tamamlandi
echo   [+] Sunucu baslatiliyor...
echo  ================================================
echo.
echo   Durdur: CTRL+C
echo.

timeout /t 2 /nobreak >nul

python app.py

echo.
echo.
echo  ================================================
echo   [OK] Sunucu durduruldu
echo  ================================================
echo.
pause

endlocal


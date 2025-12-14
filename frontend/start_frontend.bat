@echo off
echo ========================================
echo Site Guvenlik Frontend Baslatiliyor...
echo ========================================
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo node_modules bulunamadi, yukleniyor...
    call npm install
    echo.
)

echo Frontend sunucusu baslatiliyor...
echo Tarayici: http://localhost:3000
echo.
call npm run dev

pause


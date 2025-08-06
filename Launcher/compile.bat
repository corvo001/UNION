@echo off
echo ========================================
echo    Compilando UNION directamente con g++
echo ========================================

REM Verificar si existe MSys2
if not exist "C:\msys64\usr\bin\bash.exe" (
    echo ERROR: MSys2 no encontrado en C:\msys64\
    echo Instala MSys2 desde https://www.msys2.org/
    pause
    exit /b 1
)

REM Limpiar archivos anteriores
if exist UNION.exe del UNION.exe

REM Compilar directamente con g++ desde MSys2
echo Compilando main.cpp con SFML...
C:\msys64\usr\bin\bash.exe -l -c "cd '%CD%' && export PATH=/mingw64/bin:$PATH && g++ -std=c++17 -O2 -Wall -Wextra main.cpp -o UNION.exe -lsfml-graphics -lsfml-window -lsfml-system -lshell32 -luser32 -lgdi32 -lwinmm -static-libgcc -static-libstdc++"

REM Verificar resultado
if exist UNION.exe (
    echo.
    echo ========================================
    echo    Compilación exitosa!
    echo    Ejecutable creado: UNION.exe
    echo ========================================
    echo.
    echo Presiona cualquier tecla para ejecutar...
    pause >nul
    UNION.exe
) else (
    echo.
    echo ========================================
    echo    ERROR: La compilación falló
    echo ========================================
    echo.
    echo Posibles soluciones:
    echo 1. Instalar SFML en MSys2:
    echo    pacman -S mingw-w64-x86_64-sfml
    echo.
    echo 2. Verificar que tienes gcc instalado:
    echo    pacman -S mingw-w64-x86_64-gcc
    echo.
    echo 3. Abrir MSys2 MINGW64 y compilar manualmente:
    echo    g++ -std=c++17 -O2 main.cpp -o UNION.exe -lsfml-graphics -lsfml-window -lsfml-system
)

echo.
pause
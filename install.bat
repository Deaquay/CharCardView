@echo off

set "cwd=%~dp0"

cd /d "%cwd%"

setlocal enabledelayedexpansion

echo Character Card Viewer - Installation Script
echo ============================================

REM Check if exiftool exists in PATH
where exiftool >nul 2>&1
set EXIFTOOL_EXISTS=0
if %ERRORLEVEL% EQU 0 (
    echo [OK] exiftool found in PATH
    set EXIFTOOL_EXISTS=1
) else (
    echo [INFO] exiftool not found in PATH
)

REM Check if exiftool exists locally
if exist "exiftool\exiftool.exe" (
    echo [OK] exiftool found locally
    set "PATH=!CD!\exiftool;!PATH!"
) else (
    if !EXIFTOOL_EXISTS! EQU 0 (
        echo [INFO] exiftool not found, downloading...
        if not exist "exiftool" mkdir exiftool
        
        REM Download exiftool from GitHub releases
        set "EXIFTOOL_URL=https://github.com/Deaquay/CharCardView/releases/download/exiftool/exiftool.exe"
        set "EXIFTOOL_PATH=exiftool\exiftool.exe"
        
        REM Try curl first (available on Windows 10+)
        where curl >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            echo [INFO] Downloading with curl...
            curl -L -o "!EXIFTOOL_PATH!" "!EXIFTOOL_URL!"
        ) else (
            REM Fall back to PowerShell
            echo [INFO] Downloading with PowerShell...
            powershell -Command "Invoke-WebRequest -Uri '!EXIFTOOL_URL!' -OutFile '!EXIFTOOL_PATH!'"
        )
        
        if exist "!EXIFTOOL_PATH!" (
            echo [OK] exiftool downloaded successfully
            set "PATH=!CD!\exiftool;!PATH!"
        ) else (
            echo [ERROR] Failed to download exiftool
            echo Please download manually from: !EXIFTOOL_URL!
            pause
            exit /b 1
        )
    )
)

REM Check if uv exists
where uv >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] uv found
    set USE_UV=1
) else (
    echo [INFO] uv not found, will use pip
    set USE_UV=0
)

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH
    echo Please install Python 3.12 or later
    pause
    exit /b 1
)

python --version
echo.

REM Check if conda environment is active
if defined CONDA_PREFIX (
    echo [OK] Conda environment detected: %CONDA_PREFIX%
    echo [INFO] Skipping venv creation, using conda environment
    echo [INFO] Installing dependencies with pip...
    
    REM Create requirements.txt from pyproject.toml if it doesn't exist
    if not exist "requirements.txt" (
        echo [INFO] Creating requirements.txt...
        echo PySide6>=6.6.0 > requirements.txt
        echo Pillow>=10.0.0 >> requirements.txt
    )
    
    pip install -r requirements.txt
) else (
    REM Create virtual environment if needed
    if !USE_UV! EQU 1 (
        echo [INFO] Using uv for package management
        if not exist ".venv" (
            echo [INFO] Creating virtual environment with uv...
            uv venv
        )
        echo [INFO] Installing dependencies with uv...
        uv pip install -r requirements.txt
    ) else (
        echo [INFO] Using pip for package management
        if not exist "venv" (
            echo [INFO] Creating virtual environment...
            python -m venv venv
        )
        echo [INFO] Activating virtual environment...
        call venv\Scripts\activate.bat
        echo [INFO] Installing dependencies with pip...
        
        REM Create requirements.txt from pyproject.toml if it doesn't exist
        if not exist "requirements.txt" (
            echo [INFO] Creating requirements.txt...
            echo PySide6>=6.6.0 > requirements.txt
            echo Pillow>=10.0.0 >> requirements.txt
        )
        
        pip install -r requirements.txt
    )
)

echo.
echo [SUCCESS] Installation complete!
echo.
echo To run the application, use start.bat
pause


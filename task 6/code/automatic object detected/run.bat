@echo off
REM Batch script to run Vehicle Detection System on Windows

cls
echo ================================================
echo   AUTOMATIC VEHICLE DETECTION SYSTEM
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
pip show ultralytics >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Select an option:
echo 1. Open GUI (Graphical Interface)
echo 2. Process video/image (Command Line)
echo 3. Live Webcam Detection (Real-time)
echo 4. Fix PyTorch/CUDA errors
echo 5. Install/Update dependencies
echo 6. Test installation
echo 7. Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo Opening GUI...
    python gui.py
) else if "%choice%"=="2" (
    set /p input="Enter input file path: "
    if exist "%input%" (
        python main.py "%input%"
    ) else (
        echo Error: File not found: %input%
    )
) else if "%choice%"=="3" (
    echo Starting live webcam detection...
    python live_webcam.py
) else if "%choice%"=="4" (
    echo Running PyTorch fix...
    python fix_pytorch.py
) else if "%choice%"=="5" (
    echo Installing/Updating dependencies...
    pip install --upgrade -r requirements.txt
    echo Installation complete!
) else if "%choice%"=="6" (
    echo Testing installation...
    python test_installation.py
) else if "%choice%"=="7" (
    exit /b 0
) else (
    echo Invalid choice!
)

pause

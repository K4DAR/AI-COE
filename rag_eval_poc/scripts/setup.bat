@echo off
REM RAG Bot Web UI Setup Script for Windows

echo.
echo  RAG Bot Web UI Setup
echo =======================
echo.

REM Check Python version
echo 📦 Checking Python version...
python --version
if errorlevel 1 (
    echo  Python not found! Please install Python 3.9+ from python.org
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

REM Install dependencies
echo 📦 Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo  Failed to install dependencies
    exit /b 1
)
echo ✓ Dependencies installed

REM Create necessary directories
echo 📦 Creating directories...
if not exist "data\documents" mkdir data\documents
if not exist "chroma_db" mkdir chroma_db
if not exist ".streamlit" mkdir .streamlit
echo ✓ Directories created

REM Check for .env file
if not exist ".env" (
    echo.
    echo   No .env file found!
    echo.
    echo Create .env file with:
    echo   OPENAI_API_KEY=sk-your-api-key
    echo   OPENAI_MODEL=gpt-4o
    echo.
)

echo.
echo  Setup complete!
echo.
echo To start the web UI, run:
echo.
echo    streamlit run app.py
echo.
echo The app will open at: http://localhost:8501
echo.
pause

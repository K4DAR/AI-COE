#!/bin/bash
# RAG Bot Web UI Setup Script

echo " RAG Bot Web UI Setup"
echo "======================="
echo ""

# Check Python version
echo "📦 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create necessary directories
echo "📦 Creating directories..."
mkdir -p data/documents
mkdir -p chroma_db
mkdir -p .streamlit
echo "✓ Directories created"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "  No .env file found!"
    echo ""
    echo "Create .env file with:"
    echo "  OPENAI_API_KEY=sk-your-api-key"
    echo "  OPENAI_MODEL=gpt-4o"
    echo ""
fi

echo ""
echo " Setup complete!"
echo ""
echo "To start the web UI, run:"
echo ""
echo "   streamlit run app.py"
echo ""
echo "The app will open at: http://localhost:8501"
echo ""

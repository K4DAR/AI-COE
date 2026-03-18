#!/usr/bin/env python
"""
Main entry point for running the FastAPI server
Handles path setup for the restructured project
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Set working directory to src
os.chdir(str(src_path))

# Now import and run the API
if __name__ == "__main__":
    import uvicorn
    from api import app
    
    print(" Starting FastAPI server on http://0.0.0.0:8000")
    print("API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

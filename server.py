"""
Email Classifier Assistant - Production Server v2.0
Memory-optimized architecture for low-resource environments.
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.api.routes import app
from backend.config import PORT, ENVIRONMENT

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Email Classifier Assistant v2.0")
    print("=" * 60)
    print(f"Environment: {ENVIRONMENT}")
    print(f"Port: {PORT}")
    print("Memory Optimized: ✓")
    print("Zero-Shot Transformer: Disabled (saves ~1GB RAM)")
    print("Primary Classifier: TF-IDF (~10MB RAM)")
    print("=" * 60)
    
    host = "0.0.0.0" if ENVIRONMENT == "production" else "127.0.0.1"
    
    uvicorn.run(
        "server_v2:app",
        host=host,
        port=PORT,
        reload=(ENVIRONMENT == "development")
    )

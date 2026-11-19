"""
Main startup runner for Explainable NLP Industrial Equipment Failure Prediction.
Starts the unified FastAPI backend and static frontend server via Uvicorn.

Usage:
    python run.py
"""

import os
import sys
from pathlib import Path
import uvicorn

# Ensure the project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Pre-flight check: ensure NLP model is trained and ready
from app.model import load_nlp_model


def main():
    print("=" * 65)
    print("  Industrial Equipment Failure Prediction System")
    print("  Explainable NLP-Based Maintenance Observation Analysis")
    print("=" * 65)

    # Pre-flight check
    print("[*] Validating FMC-MWO2KG dataset and loading NLP classification model...")
    load_nlp_model()
    print("[*] NLP Model verified.")

    # Retrieve port from environment (Render deployment compatibility) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"[*] Starting server at http://localhost:{port}")
    print(f"[*] API Documentation at http://localhost:{port}/docs")
    print("=" * 65)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()

"""
FastAPI application entrypoint for Explainable NLP Industrial Failure Prediction.
Serves API routes and mounts static frontend assets for single-command execution.
"""

from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router as api_router
from app.model import load_nlp_model
from app.dataset_loader import load_all_splits, BASE_DIR

FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager: ensures FMC-MWO2KG dataset is loaded and NLP models are ready.
    """
    print("[INFO] Initializing Explainable NLP Industrial Failure Prediction service...")
    try:
        load_all_splits()
        load_nlp_model()
        print("[INFO] FMC-MWO2KG dataset and NLP classification models ready.")
    except Exception as e:
        print(f"[WARNING] Initialization check: {e}")
    yield
    print("[INFO] Application shutting down.")


app = FastAPI(
    title="Explainable NLP Industrial Equipment Failure Prediction API",
    description="Explainable NLP-Based Industrial Equipment Failure Prediction for Sustainable Maintenance",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for maximum client compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API endpoints
app.include_router(api_router)

# Mount frontend static folders
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/", include_in_schema=False)
def serve_index():
    """
    Serve the frontend single-page dashboard.
    """
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend index.html not found. Ensure frontend folder exists."}

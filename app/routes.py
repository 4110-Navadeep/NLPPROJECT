"""
FastAPI Routes for Explainable NLP Industrial Equipment Failure Prediction.
Endpoints:
- GET /api/health
- GET /api/dashboard
- POST /api/analyse
- GET /api/dataset
- GET /api/performance
- POST /api/retrain
- POST /api/report
- GET /api/reports/{filename}
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.dataset_loader import get_dataset_summary, query_dataset, BASE_DIR
from app.model import (
    predict_maintenance_report,
    get_model_performance,
    train_and_save_nlp_model,
    load_nlp_model,
    NLP_MODEL_PATH,
)
from app.pdf_report import generate_maintenance_pdf, REPORTS_DIR

router = APIRouter(prefix="/api", tags=["NLP Maintenance API"])


class AnalyseRequest(BaseModel):
    machine_id: Optional[str] = Field("MCH-101", description="Unique machine identifier")
    machine_name: Optional[str] = Field("Centrifugal Slurry Pump #2", description="Machine Name")
    equipment_type: Optional[str] = Field("Centrifugal Pump", description="Equipment Type")
    inspection_date: Optional[str] = Field(None, description="Inspection date (YYYY-MM-DD)")
    technician_name: Optional[str] = Field("Plant Technician", description="Technician Name or Badge ID")
    observation: str = Field(
        ...,
        min_length=2,
        description="Technician's natural English maintenance observation",
        examples=["Machine 1 produces extreme noise during operation. Temperature is higher than normal, vibration is increasing and the belt appears loose."],
    )


class ReportRequest(BaseModel):
    machine_id: Optional[str] = "MCH-101"
    machine_name: Optional[str] = "Centrifugal Slurry Pump #2"
    equipment_type: Optional[str] = "Centrifugal Pump"
    inspection_date: Optional[str] = None
    technician_name: Optional[str] = "Plant Technician"
    observation: str


@router.get("/health", summary="Application & NLP Model Health Status")
def health_check():
    """
    Check the status of the FastAPI backend and verify model artifact readiness.
    """
    model_ready = NLP_MODEL_PATH.exists()
    return {
        "status": "healthy",
        "service": "Explainable NLP Industrial Equipment Failure Prediction API",
        "version": "2.0.0",
        "nlp_model_ready": model_ready,
        "dataset_benchmark": "FMC-MWO2KG (502 Train, 62 Dev, 62 Test)",
    }


@router.get("/dashboard", summary="Dashboard Statistics and NLP Metrics")
def get_dashboard_data():
    """
    Return comprehensive dataset statistics and actual NLP model performance metrics
    computed from the FMC-MWO2KG benchmark dataset and trained model.
    """
    try:
        summary = get_dataset_summary()
        performance = get_model_performance()

        return {
            "dataset_summary": summary,
            "model_performance": performance,
            "workflow_steps": [
                {
                    "step": 1,
                    "title": "Technician Observation Ingestion",
                    "description": "Technicians record natural English inspection observations regarding machinery symptoms, acoustic anomalies, and operating states.",
                },
                {
                    "step": 2,
                    "title": "NLP Normalization & Feature Extraction",
                    "description": "Text is normalized (contraction expansion, abbreviation correction, negation preservation) and transformed into TF-IDF n-gram vectors.",
                },
                {
                    "step": 3,
                    "title": "Supervised Machine Learning Inference",
                    "description": "Balanced Multinomial Logistic Regression predicts the failure category with calibrated probability and low-confidence safeguards.",
                },
                {
                    "step": 4,
                    "title": "Explainability & PDF Maintenance Report",
                    "description": "Mathematical term weights explain which words influenced the prediction, paired with actionable inspection protocols and downloadable PDF reports.",
                },
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard analytics: {str(e)}",
        )


@router.post("/analyse", summary="Analyse Maintenance Observation Report")
def analyse_report(payload: AnalyseRequest):
    """
    Accepts machine metadata and technician English observation:
    - Normalizes text
    - Extracts symptoms
    - Predicts failure category & confidence
    - Identifies influential words & plain-English explanation
    - Attaches maintenance recommendations
    """
    try:
        results = predict_maintenance_report(payload.observation)
        results["machine_id"] = payload.machine_id or "MCH-101"
        results["machine_name"] = payload.machine_name or "Industrial Operating Unit"
        results["equipment_type"] = payload.equipment_type or "General Equipment"
        results["inspection_date"] = payload.inspection_date or datetime.now().strftime("%Y-%m-%d")
        results["technician_name"] = payload.technician_name or "Plant Technician"

        return {"success": True, "data": results}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@router.get("/dataset", summary="Searchable & Paginated FMC-MWO2KG Observations")
def get_dataset(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=5, le=100, description="Records per page"),
    split: str = Query("ALL", description="Filter by split ('ALL', 'Train', 'Dev', 'Test')"),
    category: str = Query("ALL", description="Filter by Failure Category"),
    search: str = Query("", description="Search term for observation text"),
):
    """
    Query the FMC-MWO2KG benchmark observations with server-side pagination, search, and category filtering.
    """
    try:
        data = query_dataset(
            page=page,
            page_size=page_size,
            split=split,
            category=category,
            search=search,
        )
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query dataset: {str(e)}",
        )


@router.get("/performance", summary="NLP Model Evaluation Metrics")
def get_performance():
    """
    Return actual holdout evaluation metrics computed on test.txt.
    """
    try:
        metrics = get_model_performance()
        return {"success": True, "data": metrics}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to retrieve model performance: {str(e)}",
        )


@router.post("/retrain", summary="Retrain NLP Failure Model")
def retrain_model():
    """
    Trigger retraining of the TF-IDF + Logistic Regression pipeline on train.txt,
    re-evaluate on test.txt, and refresh in-memory model instances.
    """
    try:
        metrics = train_and_save_nlp_model()
        return {
            "success": True,
            "message": "NLP Model successfully retrained on train.txt and re-evaluated on test.txt.",
            "data": metrics,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retraining failed: {str(e)}",
        )


@router.post("/report", summary="Generate Downloadable PDF Maintenance Report")
def create_report(payload: ReportRequest):
    """
    Generate a formal PDF maintenance analysis report using ReportLab.
    Returns the report metadata and download URL.
    """
    try:
        # Run analysis to ensure clean, accurate prediction data in report
        results = predict_maintenance_report(payload.observation)
        results["machine_id"] = payload.machine_id or "MCH-101"
        results["machine_name"] = payload.machine_name or "Industrial Operating Unit"
        results["equipment_type"] = payload.equipment_type or "General Equipment"
        results["inspection_date"] = payload.inspection_date or datetime.now().strftime("%Y-%m-%d")
        results["technician_name"] = payload.technician_name or "Plant Technician"

        pdf_path = generate_maintenance_pdf(results)
        download_url = f"/api/reports/{pdf_path.name}"

        return {
            "success": True,
            "report_id": pdf_path.stem,
            "filename": pdf_path.name,
            "download_url": download_url,
            "message": "PDF report successfully compiled.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF report generation failed: {str(e)}",
        )


@router.get("/reports/{filename}", summary="Download Generated PDF Report")
def download_report(filename: str):
    """
    Download or view a generated PDF report file.
    """
    # Prevent directory traversal attacks
    safe_name = Path(filename).name
    pdf_path = REPORTS_DIR / safe_name

    if not pdf_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report file '{safe_name}' not found or expired.",
        )

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=safe_name,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )

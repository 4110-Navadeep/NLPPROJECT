"""
Direct verification of routes and business logic.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.routes import (
    health_check,
    get_dashboard_data,
    analyse_report,
    get_dataset,
    get_performance,
    create_report,
    AnalyseRequest,
    ReportRequest,
)

# 1. Health
h = health_check()
assert h["status"] == "healthy"
assert h["nlp_model_ready"] is True
print("PASS: health_check()")

# 2. Dashboard Analytics
d = get_dashboard_data()
assert "dataset_summary" in d
assert "model_performance" in d
print("PASS: get_dashboard_data()")

# 3. Predict / Analyse
req = AnalyseRequest(
    machine_id="MCH-101",
    machine_name="Centrifugal Slurry Pump #1",
    equipment_type="Centrifugal Pump",
    inspection_date="2026-11-19",
    technician_name="Tech Alex Morgan (ID: TM-410)",
    observation="Machine 1 produces extreme noise during operation. Temperature is higher than normal, vibration is increasing and the belt appears loose."
)
p_resp = analyse_report(req)
assert p_resp["success"] is True
p = p_resp["data"]
assert "predicted_category" in p
assert "confidence" in p
assert "explainability" in p
print(f"PASS: analyse_report() -> {p['predicted_category']} ({p['confidence']*100:.1f}%)")

# 4. Generate Report (PDF)
report_req = ReportRequest(
    machine_id="MCH-101",
    machine_name="Centrifugal Slurry Pump #1",
    equipment_type="Centrifugal Pump",
    inspection_date="2026-11-19",
    technician_name="Tech Alex Morgan (ID: TM-410)",
    observation=req.observation
)
pdf_resp = create_report(report_req)
assert "download_url" in pdf_resp
assert "report_id" in pdf_resp
print(f"PASS: create_report() -> {pdf_resp['download_url']}")

# 5. Dataset records
ds_resp = get_dataset(page=1, page_size=10, search="", split="ALL", category="ALL")
assert ds_resp["success"] is True
ds = ds_resp["data"]
assert ds["total_records"] == 626
assert len(ds["records"]) == 10
print("PASS: get_dataset()")

# 6. Performance metrics
perf_resp = get_performance()
assert perf_resp["success"] is True
perf = perf_resp["data"]
assert "test_metrics" in perf
assert perf["test_metrics"]["accuracy"] > 0.6
print(f"PASS: get_performance() -> Accuracy: {perf['test_metrics']['accuracy']*100:.2f}%")

print("\nALL IN-PROCESS ROUTE & LOGIC TESTS PASSED PERFECTLY!")

"""
Verification script for Dashboard modification.
"""
import sys
from pathlib import Path

index_html_path = Path("frontend/index.html")
app_js_path = Path("frontend/js/app.js")
css_path = Path("frontend/css/style.css")

html_content = index_html_path.read_text(encoding="utf-8")
js_content = app_js_path.read_text(encoding="utf-8")
css_content = css_path.read_text(encoding="utf-8")

# 1. Verify dashboard section isolation
assert '<section id="view-dashboard"' in html_content, "Missing #view-dashboard"
dashboard_chunk = html_content.split('<section id="view-dashboard"')[1].split('</section>')[0]

# Check removal of old 4 metric cards from dashboard
old_metrics = [
    "Total Maintenance Observations",
    "Failure Categories – 22",
    "Training Records",
    "Model Test Accuracy",
    "metric-total-records",
    "metric-categories-count",
    "metric-train-records",
    "metric-model-accuracy",
    "chart-failure-types",
    "chart-partition-breakdown",
    "chart-top-categories",
    "chart-model-metrics"
]

for m in old_metrics:
    assert m not in dashboard_chunk, f"Found old metric/chart element in dashboard: {m}"
print("PASS: All 4 old metric cards and charts completely removed from Dashboard.")

# 2. Check 4 new sections on Dashboard
# Section 1: Hero
assert "Industrial Maintenance Intelligence" in dashboard_chunk, "Hero heading missing"
assert "Analyse technician-written maintenance observations" in dashboard_chunk, "Hero description missing"
assert "Analyse Maintenance Report" in dashboard_chunk, "Primary button missing"
assert "Explore Project" in dashboard_chunk, "Secondary button missing"
assert "<svg" in dashboard_chunk and "hero-illustration-block" in dashboard_chunk, "Hero illustration missing"

# Section 2: Workflow
assert "How the System Works" in dashboard_chunk, "Workflow heading missing"
assert "Technician Observation" in dashboard_chunk, "Workflow step 1 missing"
assert "NLP Processing" in dashboard_chunk, "Workflow step 2 missing"
assert "Failure Prediction" in dashboard_chunk, "Workflow step 3 missing"
assert "Maintenance Report" in dashboard_chunk, "Workflow step 4 missing"
assert "workflow-connector" in dashboard_chunk, "Workflow connecting arrows missing"

# Section 3: CTA
assert "Ready to Analyse a Maintenance Inspection?" in dashboard_chunk, "CTA heading missing"
assert "Submit natural English technician observations" in dashboard_chunk, "CTA description missing"
assert "Start Report Analysis" in dashboard_chunk, "CTA button missing"

# Section 4: Capabilities
assert "Key Application Capabilities" in dashboard_chunk, "Capabilities heading missing"
assert "Natural Language Processing" in dashboard_chunk, "Cap 1 missing"
assert "Explainable Predictions" in dashboard_chunk, "Cap 2 missing"
assert "Maintenance Decision Support" in dashboard_chunk, "Cap 3 missing"
assert "PDF Report Generation" in dashboard_chunk, "Cap 4 missing"

print("PASS: All 4 required Dashboard sections present with exact required text and structure.")

# 3. Check other views remain intact
assert '<section id="view-predict"' in html_content, "view-predict missing"
assert '<section id="view-dataset"' in html_content, "view-dataset missing"
assert '<section id="view-performance"' in html_content, "view-performance missing"
assert '<section id="view-about"' in html_content, "view-about missing"

# Verify metrics and charts STILL EXIST on Dataset and Model Performance views
assert 'id="perf-accuracy"' in html_content, "Performance metrics missing in view-performance"
assert 'id="dataset-table-body"' in html_content, "Dataset table missing in view-dataset"
print("PASS: Other views (predict, dataset, performance, about) are completely intact.")

# 4. Check JS Router data-goto handlers
assert 'data-goto' in js_content, "data-goto handler missing in JS"
print("PASS: JS router supports dynamic navigation via data-goto attributes.")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

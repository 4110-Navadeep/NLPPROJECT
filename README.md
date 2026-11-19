# Explainable NLP-Based Industrial Equipment Failure Prediction for Sustainable Maintenance

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4+-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.0+-red?style=flat&logo=adobeacrobatreader&logoColor=white)](https://www.reportlab.com/)
[![License](https://img.shields.io/badge/Academic-Capstone-blue.svg)]()

A complete, working, professional web application for an academic capstone demonstration that ingests unstructured English industrial maintenance reports, extracts diagnostic symptoms via NLP, classifies failure categories using Machine Learning, explains word-level contributions, and generates formal downloadable engineering PDF reports.

---

## 1. Project Title & Capstone Context

**Title:** Explainable NLP-Based Industrial Equipment Failure Prediction for Sustainable Maintenance  
**Domain:** Natural Language Processing (NLP), Industrial Artificial Intelligence, Sustainable Maintenance  
**Core Purpose:** Enable plant maintenance technicians to input physical inspection observations in natural English, identify probable equipment failure modes across 22 categories, inspect which words drove the classification, review prioritized inspection actions, and download a publication-ready PDF maintenance report.

---

## 2. Dataset Information: FMC-MWO2KG Benchmark

The application uses the authentic **FMC-MWO2KG** (FMC Technologies Maintenance Work Order to Knowledge Graph) benchmark dataset located at `data/FMC-MWO2KG/`:

- **Files Preserved:**
  - `train.txt`: 502 labelled maintenance work orders (Training partition - 80.2%)
  - `dev.txt`: 62 labelled maintenance work orders (Validation partition - 9.9%)
  - `test.txt`: 62 labelled maintenance work orders (Unseen Holdout Test partition - 9.9%)
- **Total Records:** 626 observations
- **Target Classes (22 Categories):**
  `Minor in-service problems`, `Breakdown`, `Structural deficiency`, `Electrical`, `Plugged / choked`, `Leaking`, `Failure to start on demand`, `Abnormal instrument reading`, `Fail to function`, `Low output`, `Vibration`, `Overheating`, `Other`, `Noise`, `Contamination`, `Failure to stop on demand`, `Erratic output`, `Spurious stop`, `High output`, `Fail to close`, `Failure to rotate`, `Fail to open`.
- **Integrity:** Original filenames, extensions, and standard splits are strictly preserved in read-only mode without modification or synthetic fabrication.

---

## 3. Technology Stack

- **Backend:** Python, FastAPI, Uvicorn, Pandas, NumPy, Scikit-learn, Joblib, Pydantic
- **NLP & Feature Engineering:** Regular Expressions, Contraction Expansion, Domain Abbreviation Normalization, Negation Token Preservation (`no`, `not`, `never`, `unable`, `failed`), Sublinear TF-IDF Vectorizer (Unigrams & Bigrams)
- **Machine Learning:** Multinomial Logistic Regression (`class_weight='balanced'`, `max_iter=1000`, `C=6.0`)
- **PDF Generation:** ReportLab (`SimpleDocTemplate`, `TableStyle`, `NumberedCanvas`)
- **Frontend:** Semantic HTML5, Custom Cloud Dashboard CSS (Light Theme only), Vanilla JavaScript (ES6+), Chart.js
- **Cloud Deployment:** Render Web Service, `render.yaml`

---

## 4. Actual Model Evaluation Results (Unseen test.txt Holdout: 62 Samples)

The model is trained exclusively on `train.txt` and evaluated on the independent holdout `test.txt`:

- **Holdout Test Accuracy:** `62.90%`
- **Macro F1-Score:** `0.4739`
- **Weighted F1-Score:** `0.6123`
- **Macro Precision:** `0.5181`
- **Macro Recall:** `0.4585`
- **Dev (Validation) Accuracy:** `54.84%`
- **Vocabulary Size:** `860 terms`

### Per-Category Performance Breakdown:

| Failure Category | Test Precision | Test Recall | Test F1-Score | Test Support |
| :--- | :---: | :---: | :---: | :---: |
| **Abnormal instrument reading** | 1.00 | 1.00 | 1.00 | 1 |
| **Breakdown** | 0.75 | 0.43 | 0.55 | 7 |
| **Contamination** | 1.00 | 1.00 | 1.00 | 1 |
| **Electrical** | 0.80 | 0.67 | 0.73 | 6 |
| **Fail to function** | 1.00 | 0.67 | 0.80 | 3 |
| **Leaking** | 1.00 | 0.67 | 0.80 | 3 |
| **Minor in-service problems** | 0.61 | 0.82 | 0.70 | 17 |
| **Other** | 1.00 | 0.50 | 0.67 | 2 |
| **Overheating** | 1.00 | 1.00 | 1.00 | 4 |
| **Plugged / choked** | 0.50 | 0.83 | 0.62 | 6 |
| **Structural deficiency** | 0.67 | 0.67 | 0.67 | 3 |

*(Zero-division classes in the holdout split with 1-2 samples reflect the natural real-world imbalance of maintenance logs).*

---

## 5. Project Structure

```
NLP PROJECT/
├── archive/
│   └── predictive_maintenance.csv        # Historical sensor CSV (preserved read-only)
├── data/
│   └── FMC-MWO2KG/
│       ├── train.txt                     # 502 training work order observations
│       ├── dev.txt                       # 62 validation observations
│       └── test.txt                      # 62 holdout test observations
├── app/
│   ├── main.py                           # FastAPI application entrypoint & static mounting
│   ├── routes.py                         # REST API endpoints & Pydantic schemas
│   ├── dataset_loader.py                 # FMC-MWO2KG loader, statistics & pagination
│   ├── text_preprocessing.py             # NLP normalization & symptom extraction
│   ├── model.py                          # TF-IDF + Logistic Regression inference pipeline
│   ├── explainability.py                 # Word contribution decomposition (W * x)
│   ├── recommendations.py                # Actionable inspection checklists for 22 categories
│   └── pdf_report.py                     # ReportLab PDF generation engine
├── frontend/
│   ├── index.html                        # Cloud maintenance dashboard single-page interface
│   ├── css/
│   │   └── style.css                     # Light enterprise dashboard styles
│   └── js/
│       └── app.js                        # Client logic, presets, Chart.js & PDF trigger
├── models/
│   ├── nlp_failure_model.joblib          # Trained Scikit-learn NLP pipeline
│   └── evaluation_metrics.json           # Actual holdout evaluation metrics
├── reports/                              # Generated PDF maintenance reports
├── scripts/
│   └── train_model.py                    # Standalone model training & evaluation script
├── requirements.txt                      # Application dependencies
├── run.py                                # Single-command unified application entrypoint
├── render.yaml                           # Render cloud deployment blueprint
├── .gitignore                            # Version control exclusion rules
└── README.md                             # Comprehensive project documentation
```

---

## 6. Single-Command Execution

The frontend and backend run together synchronously using **one single command**:

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Application
```bash
python run.py
```

### Access Points:
- **Interactive Web Application:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc API Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 7. PDF Report Generation

After submitting an inspection observation on the **Analyse Maintenance Report** page, clicking **Download PDF Report** triggers `POST /api/report`:

1. Uses ReportLab to generate a formal document titled:
   `INDUSTRIAL EQUIPMENT MAINTENANCE ANALYSIS REPORT`
2. Encodes Report ID, Inspection Date, Machine ID, Machine Name, Equipment Type, Technician Name/ID.
3. Formats original technician observations, extracted symptoms, predicted category, confidence percentage, influential words table with support/reduce directions, suggested maintenance checklists, and official disclaimer.
4. Downloads directly to the client with two-pass canvas page numbering (`Page 1 of 1`).

---

## 8. Render Cloud Deployment

The repository is pre-configured for automated deployment on Render as a single Web Service:

1. Push this repository to GitHub or GitLab.
2. In the Render Dashboard, select **New +** &rarr; **Web Service**.
3. Connect the repository.
4. Render will read `render.yaml` or use:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt && python scripts/train_model.py`
   - **Start Command:** `python run.py`
5. The application dynamically respects the `PORT` environment variable and binds to `0.0.0.0`.
6. Generated PDF reports can be downloaded immediately during the session.

---

## 9. Academic Capstone Disclaimer

This system provides statistical decision support based on supervised machine learning models trained on benchmark maintenance observations. It is intended to assist technicians in prioritizing inspections and does not guarantee physical diagnoses or replace professional engineering judgment.

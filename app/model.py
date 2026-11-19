"""
Model Training, Inference, and Evaluation Module for NLP Equipment Failure Prediction.
Trains a TF-IDF + Balanced Logistic Regression Pipeline on train.txt from FMC-MWO2KG,
evaluates on test.txt, and provides inference with confidence calibration and explainability.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

from app.dataset_loader import load_all_splits, BASE_DIR
from app.text_preprocessing import preprocess_text, extract_symptoms
from app.explainability import explain_text_prediction
from app.recommendations import get_recommendations_for_category

MODELS_DIR = BASE_DIR / "models"
NLP_MODEL_PATH = MODELS_DIR / "nlp_failure_model.joblib"
METRICS_PATH = MODELS_DIR / "evaluation_metrics.json"

# In-memory cached model and metrics
_NLP_MODEL: Optional[Pipeline] = None
_EVALUATION_METRICS: Optional[Dict[str, Any]] = None

CONFIDENCE_WARNING_THRESHOLD = 0.30  # 30% probability threshold for 22-class model


def train_and_save_nlp_model() -> Dict[str, Any]:
    """
    Train TF-IDF + Logistic Regression pipeline strictly on train.txt,
    evaluate on unseen holdout test.txt, and persist artifacts inside models/.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    splits = load_all_splits(force_reload=True)

    train_df = splits["train"].copy()
    dev_df = splits["dev"].copy()
    test_df = splits["test"].copy()

    # Preprocess text
    train_df["clean_text"] = train_df["text"].apply(preprocess_text)
    dev_df["clean_text"] = dev_df["text"].apply(preprocess_text)
    test_df["clean_text"] = test_df["text"].apply(preprocess_text)

    X_train = train_df["clean_text"]
    y_train = train_df["label"]

    X_test = test_df["clean_text"]
    y_test = test_df["label"]

    # Construct pipeline: TF-IDF with unigrams & bigrams + Balanced Logistic Regression
    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=1,
                sublinear_tf=True,
                strip_accents="unicode",
            ),
        ),
        (
            "clf",
            LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=42,
                solver="lbfgs",
                C=6.0,
            ),
        ),
    ])

    # Fit exclusively on train split
    pipeline.fit(X_train, y_train)

    # Evaluate on test split
    y_test_pred = pipeline.predict(X_test)
    classes = list(pipeline.named_steps["clf"].classes_)

    test_acc = float(accuracy_score(y_test, y_test_pred))
    test_macro_prec = float(precision_score(y_test, y_test_pred, average="macro", zero_division=0))
    test_weighted_prec = float(precision_score(y_test, y_test_pred, average="weighted", zero_division=0))
    test_macro_rec = float(recall_score(y_test, y_test_pred, average="macro", zero_division=0))
    test_weighted_rec = float(recall_score(y_test, y_test_pred, average="weighted", zero_division=0))
    test_macro_f1 = float(f1_score(y_test, y_test_pred, average="macro", zero_division=0))
    test_weighted_f1 = float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_test, y_test_pred, labels=classes).tolist()
    class_report = classification_report(y_test, y_test_pred, output_dict=True, zero_division=0)

    # Validation (dev) check
    y_dev_pred = pipeline.predict(dev_df["clean_text"])
    dev_acc = float(accuracy_score(dev_df["label"], y_dev_pred))

    metrics_payload = {
        "model_name": "TF-IDF + Balanced Multinomial Logistic Regression",
        "dataset_split_info": {
            "train_samples": len(train_df),
            "dev_samples": len(dev_df),
            "test_samples": len(test_df),
            "split_policy": "Original FMC-MWO2KG benchmark partitions strictly preserved",
        },
        "test_metrics": {
            "accuracy": round(test_acc, 4),
            "macro_precision": round(test_macro_prec, 4),
            "weighted_precision": round(test_weighted_prec, 4),
            "macro_recall": round(test_macro_rec, 4),
            "weighted_recall": round(test_weighted_rec, 4),
            "macro_f1": round(test_macro_f1, 4),
            "weighted_f1": round(test_weighted_f1, 4),
            "dev_accuracy": round(dev_acc, 4),
        },
        "classes": classes,
        "confusion_matrix": {
            "matrix": cm,
            "classes": classes,
        },
        "classification_report": class_report,
        "vocabulary_size": int(len(pipeline.named_steps["tfidf"].vocabulary_)),
        "methodology": {
            "vectorization": "TF-IDF Vectorizer (Unigrams & Bigrams, Sublinear TF scaling)",
            "classification": "Multinomial Logistic Regression with inverse-frequency balanced class weights",
            "imbalance_handling": "Inverse class weighting ensures low-frequency maintenance categories receive adequate optimization penalty",
            "leakage_prevention": "Model fitted exclusively on train.txt; evaluation strictly conducted on test.txt",
        },
    }

    # Persist model and metrics
    joblib.dump(pipeline, NLP_MODEL_PATH)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    global _NLP_MODEL, _EVALUATION_METRICS
    _NLP_MODEL = pipeline
    _EVALUATION_METRICS = metrics_payload

    return metrics_payload


def load_nlp_model(force_reload: bool = False) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Load saved NLP pipeline and evaluation metrics from disk.
    Auto-trains if model artifacts are not present.
    """
    global _NLP_MODEL, _EVALUATION_METRICS
    if not force_reload and _NLP_MODEL is not None and _EVALUATION_METRICS is not None:
        return _NLP_MODEL, _EVALUATION_METRICS

    if not NLP_MODEL_PATH.exists() or not METRICS_PATH.exists():
        train_and_save_nlp_model()

    _NLP_MODEL = joblib.load(NLP_MODEL_PATH)
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        _EVALUATION_METRICS = json.load(f)

    return _NLP_MODEL, _EVALUATION_METRICS


def get_model_performance() -> Dict[str, Any]:
    """
    Retrieve persisted model performance metrics.
    """
    _, metrics = load_nlp_model()
    return metrics


def predict_maintenance_report(observation_text: str) -> Dict[str, Any]:
    """
    Execute full NLP inference on a technician's natural English maintenance observation:
    1. Normalizes raw text.
    2. Extracts diagnostic symptoms & keywords.
    3. Infers failure category probabilities.
    4. Evaluates prediction confidence and checks for low confidence.
    5. Decomposes feature contributions for explainability.
    6. Attaches actionable inspection recommendations.
    """
    clean_obs = observation_text.strip()
    if not clean_obs:
        raise ValueError("Technician maintenance observation cannot be empty.")

    pipeline, _ = load_nlp_model()
    normalized_text = preprocess_text(clean_obs)

    # Inference
    predicted_category = str(pipeline.predict([normalized_text])[0])
    probabilities = pipeline.predict_proba([normalized_text])[0]
    classes = list(pipeline.named_steps["clf"].classes_)

    # Format class probabilities
    all_probs = []
    for cls_name, prob in zip(classes, probabilities):
        all_probs.append({
            "category": cls_name,
            "probability": round(float(prob), 4),
            "percentage": round(float(prob) * 100, 2),
        })

    all_probs.sort(key=lambda x: x["probability"], reverse=True)
    top_pred = all_probs[0]
    confidence_prob = top_pred["probability"]
    confidence_pct = top_pred["percentage"]

    # Secondary probable alternatives
    alternatives = [ap for ap in all_probs if ap["category"] != predicted_category][:3]

    # Low-confidence detection
    is_low_confidence = False
    low_confidence_msg = None
    if confidence_prob < CONFIDENCE_WARNING_THRESHOLD:
        is_low_confidence = True
        low_confidence_msg = (
            f"Low Confidence Warning ({confidence_pct}%): Multiple failure categories show close statistical probability. "
            "Technician should conduct comprehensive manual physical inspection."
        )
    elif len(all_probs) > 1 and (confidence_prob - all_probs[1]["probability"]) < 0.05:
        is_low_confidence = True
        low_confidence_msg = (
            f"Close Alternative Detected: Primary prediction ({top_pred['category']}: {confidence_pct}%) is closely matched "
            f"by alternative category ({all_probs[1]['category']}: {all_probs[1]['percentage']}%)."
        )

    # Symptom extraction
    detected_symptoms = extract_symptoms(clean_obs)

    # Mathematical explainability decomposition
    explanation = explain_text_prediction(
        pipeline=pipeline,
        raw_text=clean_obs,
        predicted_class=predicted_category,
    )

    # Maintenance inspection guidance
    recommendations = get_recommendations_for_category(predicted_category)

    return {
        "original_text": clean_obs,
        "normalized_text": normalized_text,
        "predicted_category": predicted_category,
        "confidence": confidence_prob,
        "confidence_percentage": confidence_pct,
        "is_low_confidence": is_low_confidence,
        "low_confidence_warning": low_confidence_msg,
        "alternative_categories": alternatives,
        "detected_symptoms": detected_symptoms,
        "explainability": explanation,
        "maintenance_recommendations": recommendations,
        "all_probabilities": all_probs[:8],
    }

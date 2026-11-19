"""
Standalone Training Script for FMC-MWO2KG NLP Failure Prediction Model.
Usage:
    python scripts/train_model.py

Loads data/FMC-MWO2KG/train.txt, trains TF-IDF + Balanced Logistic Regression pipeline,
evaluates on test.txt, and saves models/nlp_failure_model.joblib and models/evaluation_metrics.json.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.model import train_and_save_nlp_model


def main():
    print("=" * 65)
    print("  FMC-MWO2KG NLP Failure Prediction Model Training")
    print("  Explainable Machine Learning for Sustainable Maintenance")
    print("=" * 65)
    print(f"Working Directory: {BASE_DIR}")
    print("Training pipeline on data/FMC-MWO2KG/train.txt...")

    try:
        metrics = train_and_save_nlp_model()
        test_m = metrics["test_metrics"]
        split_m = metrics["dataset_split_info"]

        print("\n[SUCCESS] Model training and holdout evaluation completed successfully!")
        print("\n" + "-" * 50)
        print("DATASET PARTITION SIZES")
        print("-" * 50)
        print(f"Train records:       {split_m['train_samples']}")
        print(f"Dev (val) records:   {split_m['dev_samples']}")
        print(f"Test records:        {split_m['test_samples']}")
        print(f"Total vocabulary:    {metrics['vocabulary_size']} terms")

        print("\n" + "-" * 50)
        print("HOLDOUT TEST EVALUATION METRICS (test.txt: 62 samples)")
        print("-" * 50)
        print(f"Test Accuracy:       {test_m['accuracy'] * 100:.2f}%")
        print(f"Test Macro F1:       {test_m['macro_f1']:.4f}")
        print(f"Test Weighted F1:    {test_m['weighted_f1']:.4f}")
        print(f"Test Macro Precision:{test_m['macro_precision']:.4f}")
        print(f"Test Macro Recall:   {test_m['macro_recall']:.4f}")
        print(f"Dev Validation Acc:  {test_m['dev_accuracy'] * 100:.2f}%")

        print("\n" + "-" * 50)
        print(f"EVALUATED CATEGORIES ({len(metrics['classes'])}):")
        print("-" * 50)
        for cls_name in metrics["classes"]:
            c_data = metrics["classification_report"].get(cls_name, {})
            p = c_data.get("precision", 0)
            r = c_data.get("recall", 0)
            f = c_data.get("f1-score", 0)
            s = c_data.get("support", 0)
            if s > 0:
                print(f"  - {cls_name:32s} | P: {p:.2f} | R: {r:.2f} | F1: {f:.2f} | Test Support: {int(s)}")

        print("\n" + "-" * 50)
        print("Persisted Artifacts:")
        print(f"  - {BASE_DIR / 'models' / 'nlp_failure_model.joblib'}")
        print(f"  - {BASE_DIR / 'models' / 'evaluation_metrics.json'}")
        print("=" * 65)

    except Exception as e:
        print(f"\n[ERROR] Model training failed: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

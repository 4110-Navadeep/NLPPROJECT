"""
Explainability Module for NLP-Based Industrial Equipment Failure Prediction.
Decomposes Logistic Regression class coefficients and TF-IDF feature weights
to explain which technician observation terms influenced the predicted failure category.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.pipeline import Pipeline
from app.text_preprocessing import preprocess_text


def explain_text_prediction(
    pipeline: Pipeline,
    raw_text: str,
    predicted_class: str,
) -> Dict[str, Any]:
    """
    Compute word-level and n-gram contributions for the predicted failure category.
    
    Contribution: c_j = W_{k, j} * x_j
    Where:
      - x_j is the TF-IDF weight of term j in the preprocessed observation.
      - W_{k, j} is the trained Logistic Regression coefficient for class k and term j.
    """
    tfidf = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["clf"]

    cleaned_text = preprocess_text(raw_text)
    feature_names = tfidf.get_feature_names_out()
    classes = list(clf.classes_)

    if predicted_class not in classes:
        return {
            "top_words": [],
            "all_active_words": [],
            "supporting_words": [],
            "opposing_words": [],
            "narrative_explanation": f"Unable to compute explanation for unindexed class: {predicted_class}.",
            "disclaimer": "Feature weights indicate statistical influence in the model and do not prove physical causation.",
        }

    class_idx = classes.index(predicted_class)
    coefs = clf.coef_[class_idx]

    # Transform preprocessed text
    x_transformed = tfidf.transform([cleaned_text]).toarray()[0]

    active_indices = np.where(x_transformed > 0)[0]
    active_terms = []

    for idx in active_indices:
        term = feature_names[idx]
        tfidf_val = float(x_transformed[idx])
        coef = float(coefs[idx])
        contrib = float(tfidf_val * coef)
        abs_contrib = abs(contrib)
        is_positive = contrib > 0
        direction = "Supports predicted category" if is_positive else "Reduces category likelihood"

        active_terms.append({
            "term": term,
            "tfidf_weight": round(tfidf_val, 4),
            "coefficient": round(coef, 4),
            "contribution": round(contrib, 4),
            "abs_contribution": round(abs_contrib, 4),
            "direction": direction,
            "is_positive": is_positive,
        })

    # Sort descending by absolute impact
    active_terms.sort(key=lambda item: item["abs_contribution"], reverse=True)

    # Assign qualitative contribution descriptions
    levels = ["High contribution", "Moderate contribution", "Supporting contribution", "Contextual term"]
    for i, item in enumerate(active_terms):
        item["contribution_level"] = levels[min(i, len(levels) - 1)]

    top_terms = active_terms[:6]
    supporting = [t for t in active_terms if t["is_positive"]]
    opposing = [t for t in active_terms if not t["is_positive"]]

    # Construct plain-English academic explanation narrative
    if not supporting:
        if active_terms:
            top_term_names = ", ".join([f"'{t['term']}'" for t in active_terms[:3]])
            narrative = (
                f"The observation words ({top_term_names}) do not show strong positive historical correlation "
                f"with '{predicted_class}'. The classification was assigned as the closest statistical profile."
            )
        else:
            narrative = (
                f"No specific diagnostic failure terms from the training vocabulary were detected in the observation. "
                f"The system classified the report into '{predicted_class}' based on baseline prior distributions."
            )
    else:
        support_phrases = [
            f"'{t['term']}' ({t['contribution_level'].lower()}, score: {t['contribution']:+.3f})"
            for t in supporting[:3]
        ]
        narrative = (
            f"The prediction for '{predicted_class}' is primarily supported by the occurrence of {', '.join(support_phrases)}. "
        )
        if opposing:
            oppose_phrases = [f"'{t['term']}'" for t in opposing[:2]]
            narrative += f"Conversely, the presence of {', '.join(oppose_phrases)} counter-balanced the classification score. "

        narrative += (
            "Note: These contributions reflect trained linguistic associations between technician "
            "descriptions and historical maintenance work orders, and do not represent physical proof of causation."
        )

    return {
        "top_words": top_terms,
        "all_active_words": active_terms,
        "supporting_words": supporting[:5],
        "opposing_words": opposing[:5],
        "narrative_explanation": narrative,
        "disclaimer": "Feature weights indicate statistical influence in the model and do not prove physical causation.",
    }

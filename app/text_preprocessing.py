"""
NLP Text Preprocessing Module for Industrial Equipment Maintenance Reports.
Normalizes technician observations, handles contractions & technical abbreviations,
preserves domain-critical negation words, and extracts key maintenance symptoms.
"""

import re
from typing import List, Dict, Set, Tuple, Any

# Contraction normalization mapping
CONTRACTIONS: Dict[str, str] = {
    r"\bwont\b": "will not",
    r"\bwon\'t\b": "will not",
    r"\bcant\b": "cannot",
    r"\bcan\'t\b": "cannot",
    r"\bdoesnt\b": "does not",
    r"\bdoesn\'t\b": "does not",
    r"\bdidnt\b": "did not",
    r"\bdidn\'t\b": "did not",
    r"\bisnt\b": "is not",
    r"\bisn\'t\b": "is not",
    r"\barent\b": "are not",
    r"\baren\'t\b": "are not",
    r"\bhavent\b": "have not",
    r"\bhasnt\b": "has not",
    r"\bwouldnt\b": "would not",
    r"\bcouldnt\b": "could not",
}

# Domain abbreviations and common technician shorthand variations
MAINTENANCE_ABBREVIATIONS: Dict[str, str] = {
    r"\bcorr\b": "corrosion",
    r"\bcorroded\b": "corrosion",
    r"\bcorroding\b": "corrosion",
    r"\bvib\b": "vibration",
    r"\bvibrations\b": "vibration",
    r"\btemp\b": "temperature",
    r"\bpress\b": "pressure",
    r"\belec\b": "electrical",
    r"\brot\b": "rotation",
    r"\bshu\b": "shut",
    r"\btriping\b": "tripping",
    r"\bsiezed\b": "seized",
    r"\bspaying\b": "spraying",
    r"\bsqueeling\b": "squealing",
    r"\bvolts\b": "voltage",
    r"\brpm\b": "rotational speed",
    r"\binspecti\b": "inspection",
    r"\bcommunicatiing\b": "communicating",
    r"\bvoilently\b": "violently",
    r"\bexcessivly\b": "excessively",
    r"\bdpr\b": "damper",
}

# Symptom keywords lexicon for heuristic symptom extraction
SYMPTOM_LEXICON: Dict[str, List[str]] = {
    "Acoustic / Noise Anomaly": ["noise", "squeal", "squealing", "grinding", "rattle", "knocking", "screech", "humming"],
    "Thermal / Overheating": ["overheating", "over heat", "hot", "smoking", "temperature", "burnt", "burn", "thermal"],
    "Vibration / Imbalance": ["vibration", "shaking", "rocking", "shuddering", "wobble", "oscillating"],
    "Fluid Leakage": ["leak", "leaking", "spraying", "spilling", "seeping", "dripping", "slurry", "oil", "fluid"],
    "Blockage / Pressure Defect": ["blocked", "blockage", "plugged", "choked", "clogged", "no pressure", "descale", "restriction"],
    "Electrical / Power Fault": ["trip", "tripped", "tripping", "earth", "resistance", "short", "power", "spark", "breaker", "fuse", "voltage", "current"],
    "Structural / Mechanical Wear": ["corrosion", "corroded", "wear", "worn", "crack", "cracked", "damage", "shredded", "ripped", "bent", "loose", "seized", "broken"],
    "Functional Operation Failure": ["failed", "will not start", "cannot start", "does not work", "not working", "stopped", "stiff", "jammed", "unserviceable", "unable to run"],
}

# Critical negation and directional words that MUST be preserved during tokenization
PRESERVED_WORDS: Set[str] = {
    "no",
    "not",
    "never",
    "unable",
    "failed",
    "fail",
    "without",
    "high",
    "low",
    "hot",
    "excessive",
    "abnormal",
}


def preprocess_text(text: str) -> str:
    """
    Standardize raw technician maintenance text:
    1. Lowercases the string.
    2. Expands common verbal contractions.
    3. Normalizes technical abbreviations and common typo variants.
    4. Strips non-alphanumeric punctuation while keeping whitespace.
    5. Collapses redundant spaces.
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = text.lower()

    # Contraction expansion
    for pattern, repl in CONTRACTIONS.items():
        cleaned = re.sub(pattern, repl, cleaned)

    # Shorthand / typo normalization
    for pattern, repl in MAINTENANCE_ABBREVIATIONS.items():
        cleaned = re.sub(pattern, repl, cleaned)

    # Remove special punctuation but keep alphanumeric and spaces
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)

    # Collapse consecutive whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def extract_symptoms(text: str) -> List[Dict[str, Any]]:
    """
    Identify key equipment maintenance symptoms present in the observation.
    Returns categorized symptom matches to display in prediction cards and PDF reports.
    """
    if not text:
        return []

    norm_text = preprocess_text(text)
    detected = []

    for category, keywords in SYMPTOM_LEXICON.items():
        matched_kw = []
        for kw in keywords:
            # Word boundary regex search
            if re.search(r"\b" + re.escape(kw) + r"\b", norm_text):
                matched_kw.append(kw)

        if matched_kw:
            detected.append({
                "symptom_category": category,
                "matched_terms": matched_kw,
            })

    return detected

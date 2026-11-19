"""
Dataset loader for FMC-MWO2KG Maintenance Work Order Dataset.
Safely loads and inspects the three dataset splits (train.txt, dev.txt, test.txt)
without modifying the original downloaded files.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Resolve project base directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "FMC-MWO2KG"

TRAIN_PATH = DATA_DIR / "train.txt"
DEV_PATH = DATA_DIR / "dev.txt"
TEST_PATH = DATA_DIR / "test.txt"

# Cached DataFrames
_CACHED_SPLITS: Optional[Dict[str, pd.DataFrame]] = None


def load_raw_split(filepath: Path, split_name: str) -> pd.DataFrame:
    """
    Safely load a single FMC-MWO2KG split file.
    Format: text,label
    """
    if not filepath.exists():
        raise FileNotFoundError(
            f"Dataset file '{filepath.name}' not found at {filepath}. "
            "Please ensure the FMC-MWO2KG files are in data/FMC-MWO2KG/."
        )

    records = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line_str = line.strip()
            if not line_str:
                continue
            parts = line_str.rsplit(",", 1)
            if len(parts) == 2:
                text = parts[0].strip()
                label = parts[1].strip()
                if text and label:
                    records.append({
                        "id": f"{split_name.lower()}_{len(records) + 1}",
                        "text": text,
                        "label": label,
                        "split": split_name,
                    })

    df = pd.DataFrame(records)
    return df


def load_all_splits(force_reload: bool = False) -> Dict[str, pd.DataFrame]:
    """
    Load train, dev, and test splits into memory.
    """
    global _CACHED_SPLITS
    if _CACHED_SPLITS is not None and not force_reload:
        return _CACHED_SPLITS

    train_df = load_raw_split(TRAIN_PATH, "Train")
    dev_df = load_raw_split(DEV_PATH, "Dev")
    test_df = load_raw_split(TEST_PATH, "Test")

    combined_df = pd.concat([train_df, dev_df, test_df], ignore_index=True)

    _CACHED_SPLITS = {
        "train": train_df,
        "dev": dev_df,
        "test": test_df,
        "all": combined_df,
    }
    return _CACHED_SPLITS


def get_dataset_summary() -> Dict[str, Any]:
    """
    Compute comprehensive dataset statistics across all splits for the dashboard.
    """
    splits = load_all_splits()
    train_df = splits["train"]
    dev_df = splits["dev"]
    test_df = splits["test"]
    all_df = splits["all"]

    # Category counts
    all_categories = sorted(all_df["label"].unique().tolist())
    train_dist = train_df["label"].value_counts().to_dict()
    dev_dist = dev_df["label"].value_counts().to_dict()
    test_dist = test_df["label"].value_counts().to_dict()
    all_dist = all_df["label"].value_counts().to_dict()

    # Calculate average observation length in words
    avg_words = float(all_df["text"].apply(lambda t: len(t.split())).mean())

    return {
        "dataset_name": "FMC-MWO2KG Industrial Maintenance Work Orders",
        "dataset_source": "FMC-MWO2KG Benchmark (FMC Technologies Maintenance Records)",
        "file_names": ["train.txt", "dev.txt", "test.txt"],
        "total_records": len(all_df),
        "train_records": len(train_df),
        "dev_records": len(dev_df),
        "test_records": len(test_df),
        "num_categories": len(all_categories),
        "categories": all_categories,
        "all_distribution": all_dist,
        "train_distribution": train_dist,
        "dev_distribution": dev_dist,
        "test_distribution": test_dist,
        "split_proportions": {
            "Train": round((len(train_df) / len(all_df)) * 100, 1),
            "Dev (Validation)": round((len(dev_df) / len(all_df)) * 100, 1),
            "Test (Evaluation)": round((len(test_df) / len(all_df)) * 100, 1),
        },
        "average_word_count": round(avg_words, 1),
    }


def query_dataset(
    page: int = 1,
    page_size: int = 20,
    split: str = "ALL",
    category: str = "ALL",
    search: str = "",
) -> Dict[str, Any]:
    """
    Paginated, searchable, and filtered query of the maintenance observations.
    """
    splits = load_all_splits()
    df = splits["all"].copy()

    if split and split.upper() != "ALL":
        df = df[df["split"].str.upper() == split.strip().upper()]

    if category and category.upper() != "ALL":
        df = df[df["label"] == category.strip()]

    if search:
        search_str = search.strip().lower()
        df = df[df["text"].str.lower().str.contains(search_str, regex=False)]

    total_records = len(df)
    page = max(1, page)
    page_size = max(5, min(100, page_size))
    total_pages = max(1, int(np.ceil(total_records / page_size)))

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    records = df.iloc[start_idx:end_idx].to_dict(orient="records")

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": total_pages,
        "records": records,
    }

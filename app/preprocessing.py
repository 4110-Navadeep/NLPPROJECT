"""
Preprocessing module for Industrial Equipment Failure Prediction.
Defines the Scikit-learn ColumnTransformer for standardizing numerical sensor readings
and one-hot encoding categorical equipment types.
"""

from typing import Dict, Any
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from app.dataset_loader import CATEGORICAL_FEATURES, NUMERICAL_FEATURES, FEATURE_COLUMNS


def create_preprocessor() -> ColumnTransformer:
    """
    Creates and returns the Scikit-learn ColumnTransformer pipeline component.
    - StandardScaler applied to continuous sensor measurements.
    - OneHotEncoder applied to categorical equipment type ('L', 'M', 'H').
    """
    return ColumnTransformer(
        transformers=[
            (
                "num",
                StandardScaler(),
                NUMERICAL_FEATURES,
            ),
            (
                "cat",
                OneHotEncoder(
                    categories=[["H", "L", "M"]],
                    drop=None,
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


def validate_and_format_input(payload: Dict[str, Any]) -> pd.DataFrame:
    """
    Validate user-submitted sensor input dictionary and transform into a single-row DataFrame.
    """
    equipment_type = str(payload.get("equipment_type", "")).strip().upper()
    if equipment_type not in ["L", "M", "H"]:
        raise ValueError("Equipment Type must be one of: 'L', 'M', or 'H'.")

    try:
        air_temp = float(payload.get("air_temperature"))
        proc_temp = float(payload.get("process_temperature"))
        rot_speed = float(payload.get("rotational_speed"))
        torque = float(payload.get("torque"))
        tool_wear = float(payload.get("tool_wear"))
    except (TypeError, ValueError) as e:
        raise ValueError(f"All sensor readings must be valid numeric values: {str(e)}")

    # Sensible operational sanity checks
    if air_temp <= 0 or proc_temp <= 0:
        raise ValueError("Temperatures in Kelvin must be strictly positive values.")
    if rot_speed < 0 or torque < 0 or tool_wear < 0:
        raise ValueError("Rotational speed, torque, and tool wear cannot be negative.")

    data = {
        "Type": [equipment_type],
        "Air temperature [K]": [air_temp],
        "Process temperature [K]": [proc_temp],
        "Rotational speed [rpm]": [rot_speed],
        "Torque [Nm]": [torque],
        "Tool wear [min]": [tool_wear],
    }

    df = pd.DataFrame(data)[FEATURE_COLUMNS]
    return df

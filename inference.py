"""Shared trained inference model for consistent approval probability scoring."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def _generate_training_data(
    n_samples: int = 5000, seed: int = 42
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    age = rng.uniform(18.0, 75.0, size=n_samples)
    credit = rng.uniform(0.0, 100.0, size=n_samples)
    amount = rng.uniform(100.0, 20000.0, size=n_samples)

    # A stable synthetic credit process used only to train a real classifier.
    logits = (
        -2.8
        + 0.070 * credit
        - 0.020 * age
        - 0.000085 * amount
        + 0.000012 * credit * (20000.0 - amount)
    )
    probs = _sigmoid(logits)
    y = rng.binomial(1, probs)
    x = np.column_stack([age, credit, amount]).astype(np.float64)
    return x, y.astype(np.int64)


@lru_cache(maxsize=1)
def get_trained_inference_model() -> Pipeline:
    x, y = _generate_training_data()
    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )
    model.fit(x, y)
    return model


def build_feature_vector(age: float, credit_score: float, loan_amount: float) -> np.ndarray:
    return np.array([[float(age), float(credit_score), float(loan_amount)]], dtype=np.float64)


def predict_approval_probability(age: float, credit_score: float, loan_amount: float) -> float:
    model = get_trained_inference_model()
    x = build_feature_vector(age, credit_score, loan_amount)
    return float(model.predict_proba(x)[0, 1])


def predict_probabilities(x: np.ndarray) -> np.ndarray:
    """Predict probabilities for a (n_samples, 3) feature matrix."""
    if x.ndim != 2 or x.shape[1] != 3:
        raise ValueError("x must be a 2D array with exactly 3 columns: [age, credit, amount].")
    model = get_trained_inference_model()
    return model.predict_proba(x.astype(np.float64))[:, 1]


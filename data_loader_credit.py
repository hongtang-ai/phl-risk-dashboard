from __future__ import annotations

"""German Credit Data Loader."""

from typing import Tuple

import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset


def load_german_credit_data(batch_size: int = 128) -> Tuple[DataLoader, DataLoader]:
    """
    使用 UCI German Credit 数值版数据并返回 train/test dataloader。

    标签定义：
    - 原始 1 = good, 2 = bad
    - 这里映射为 1(好) / 0(坏)
    """
    url = (
        "https://archive.ics.uci.edu/ml/"
        "machine-learning-databases/statlog/german/german.data-numeric"
    )
    data = pd.read_csv(url, sep=" ", header=None)

    x = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values
    y = (y == 1).astype(float)

    scaler = StandardScaler()
    x = scaler.fit_transform(x)

    x_t = torch.tensor(x, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)

    train_x, test_x, train_y, test_y = train_test_split(
        x_t,
        y_t,
        test_size=0.2,
        random_state=42,
        stratify=y_t,
    )

    train_loader = DataLoader(
        TensorDataset(train_x, train_y),
        batch_size=batch_size,
        shuffle=True,
    )
    test_loader = DataLoader(
        TensorDataset(test_x, test_y),
        batch_size=batch_size,
        shuffle=False,
    )
    return train_loader, test_loader

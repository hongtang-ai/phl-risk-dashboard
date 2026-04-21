from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms


def _binary_targets(dataset: Dataset) -> torch.Tensor:
    ys = torch.tensor([int(dataset[i][1]) for i in range(len(dataset))], dtype=torch.long)
    return (ys > 5).float()


class IndexedDataset(Dataset):
    """包装数据集，返回 (x, index)，便于按索引读取预先计算的标签。"""

    def __init__(self, base: Dataset) -> None:
        self.base = base

    def __len__(self) -> int:
        return len(self.base)

    def __getitem__(self, idx: int):
        x, _ = self.base[idx]
        return x, idx


def load_mnist_binary(
    root: Path,
    batch_size: int,
    seed: int,
) -> tuple[DataLoader, DataLoader, torch.Tensor]:
    """加载 MNIST，并将标签映射为 (digit > 5) 二分类。"""
    tfm = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    train_ds = datasets.MNIST(root=str(root), train=True, download=True, transform=tfm)
    test_ds = datasets.MNIST(root=str(root), train=False, download=True, transform=tfm)

    train_y = _binary_targets(train_ds)
    gen = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(IndexedDataset(train_ds), batch_size=batch_size, shuffle=True, generator=gen)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader, train_y

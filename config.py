from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    """单个模型训练配置。"""

    width: int = 64
    depth: int = 3
    use_bn: bool = False
    use_residual: bool = False
    batch_size: int = 128
    epochs: int = 20
    lr: float = 1e-3


@dataclass
class SweepConfig:
    """全局扫描配置与路径。"""

    widths: list[int] = field(default_factory=lambda: [8, 16, 32, 64, 128])
    depths: list[int] = field(default_factory=lambda: [1, 2, 3, 4])
    structures: list[dict[str, bool]] = field(
        default_factory=lambda: [
            {"bn": False, "res": False},
            {"bn": True, "res": False},
            {"bn": False, "res": True},
        ]
    )
    seed: int = 42
    analysis_sample_size: int = 5000

    root_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent)

    @property
    def data_dir(self) -> Path:
        return self.root_dir / "data"

    @property
    def results_path(self) -> Path:
        return self.root_dir / "results" / "results.json"

    @property
    def plots_dir(self) -> Path:
        return self.root_dir / "plots"

from __future__ import annotations

import torch
import torch.nn as nn


def _kaiming_init(module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.kaiming_uniform_(module.weight, nonlinearity="relu")
        if module.bias is not None:
            nn.init.zeros_(module.bias)


class MLP(nn.Module):
    """支持 depth/width/BatchNorm/residual 的 MLP，前向返回 (z, h)。"""

    def __init__(
        self,
        depth: int,
        width: int,
        use_bn: bool = False,
        use_residual: bool = False,
        in_dim: int = 784,
    ) -> None:
        super().__init__()
        if depth < 1:
            raise ValueError("depth 必须 >= 1")

        self.use_residual = use_residual
        blocks: list[nn.Module] = []
        in_features = in_dim
        for _ in range(depth):
            lin = nn.Linear(in_features, width)
            bn = nn.BatchNorm1d(width) if use_bn else None
            blocks.append(nn.ModuleDict({"lin": lin, "bn": bn}))
            in_features = width

        self.blocks = nn.ModuleList(blocks)
        self.fc_out = nn.Linear(width, 1)
        self.act = nn.ReLU(inplace=True)
        self.apply(_kaiming_init)
        _kaiming_init(self.fc_out)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        x = x.view(x.size(0), -1)
        for i, block in enumerate(self.blocks):
            identity = x
            x = block["lin"](x)
            if block["bn"] is not None:
                x = block["bn"](x)
            x = self.act(x)
            if self.use_residual and i > 0 and x.shape == identity.shape:
                x = x + identity
        h = x
        z = self.fc_out(h).squeeze(-1)
        return z, h

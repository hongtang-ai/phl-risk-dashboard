# PHL（Projection–Hidden–Logit）

本项目在 MNIST 二分类任务（标签 **>5**）上训练多种 MLP，用于验证 **mid** 与投影端 logit 尺度 **σ** 之间的关系。

## 核心量

- 末层隐变量 **h**（宽度为 `width`），输出权重 **w**，标量 logit  
  **z = wᵀ h**（代码中另加偏置，分析时 **w** 取最后一层线性权重主方向）。
- **q = σ(z)**（sigmoid），经验 **mid** 定义为  
  **mid = P(|q − 0.5| ≤ ε)**，默认 **ε = 0.05**（在测试集上统计比例）。
- 将 **mid** 视作 logit 在 0 附近（对应 **q≈0.5**）的“投影密度”经验 proxy：**mid ≈ ρ_z(0)** 在离散网格上的质量。

## 理论近似

在 **z** 近似零均值、尺度为 **σ** 的光滑密度下，有  
**mid ≈ ε / σ**（小参数 / 线性化意义下的尺度律）。

更精细地，若 **z ~ N(0, σ²)**，则  
**P(|z| ≤ ε) = Φ(ε/σ) − Φ(−ε/σ)**，代码中记为 **gaussian_mid(σ)**。

## 表示几何（启发式）

经验协方差谱常呈现 **ρ_h ≈ low-rank + εI** 形态：主方向集中能量，其余方向近似各向同性噪声；有效秩  
**r = (Σλ)² / Σλ²** 用于量化“可辨识子空间”维度，并在图中标注 **r < 1.5** 的 **collapse** 区。

## Scale-invariant test

We normalize logits:

`z_norm = (z - μ) / σ`

Then recompute:

`mid_norm`

If `mid_norm` still varies across architectures:

→ `mid` depends on representation structure

Else:

→ `mid` depends on logit scale

## 运行

```bash
python main.py
# 若系统未提供 python 命令，可使用：
# python3 main.py
```

依赖：`torch`, `torchvision`, `matplotlib`, `numpy`。

## 输出

- `results/results.json`：每次实验的 **sigma, mid_raw, mid_norm, mid_sigma, r/sqrt_r, var_proj** 等记录。
- `plots/*.png`：包含基础图、scale-invariant 图、以及 `mid*σ` 与 `sqrt(r)` 的关系图。

控制台会打印每个模型的 **σ, mid_raw, mid_norm, r**（以及辅助量），并在绘图阶段打印全局 **R²**、相关系数对比与 `mid*σ` 回归统计。

# PHL 完整公式、推导与结果汇总（从开始到当前）

## 0. 项目目标

项目核心问题：验证 `mid` 是否可以理解为投影 logit 在 0 附近的密度（或质量）并被结构量（rank / 谱 / 对齐）解释。

---

## 1. 基础定义

- 隐表示：`h \in R^d`
- 输出方向：`w \in R^d`
- logit：

\[
z = w^\top h
\]

- 概率：

\[
q = \sigma(z) = \frac{1}{1+e^{-z}}
\]

- mid（经验定义，默认 `eps=0.05`）：

\[
\text{mid} = P(|q - 0.5| \le \varepsilon),\quad \varepsilon=0.05
\]

对应到实现里有两种等价计算：

1) 从 `q` 直接统计：`compute_mid_fraction(q)`  
2) 从 `z` 先做 `sigmoid` 后统计：`compute_mid_from_z(z)`

---

## 2. 与尺度相关的理论近似

### 2.1 一阶尺度律

在 0 附近密度近似平滑时，使用小区间近似：

\[
\text{mid} \approx \frac{\varepsilon}{\sigma}
\]

其中 `sigma = std(z)`。

### 2.2 高斯近似

若 `z ~ N(0, sigma^2)`，则

\[
\text{mid} \approx \Phi(\varepsilon/\sigma)-\Phi(-\varepsilon/\sigma)
\]

代码函数：`gaussian_mid(sigma)`。

---

## 3. 表示几何量（结构量）

### 3.1 投影方差

\[
\mathrm{Var}(z)=\mathrm{Var}(w^\top h)
\]

对应 `compute_projection_variance(h,w)`。

### 3.2 有效秩（协方差谱）

设 `lambda_i` 为 `Cov(h)` 特征值，则

\[
r_{eff} = \frac{(\sum_i \lambda_i)^2}{\sum_i \lambda_i^2}
\]

对应 `compute_effective_rank(h)`。

### 3.3 另一种有效秩（谱熵）

在 `spectrum_alpha_analyzer` 里还实现了熵型有效秩：

\[
p_i=\frac{\lambda_i}{\sum_j\lambda_j},\quad
r_{ent}=\exp\left(-\sum_i p_i\log p_i\right)
\]

---

## 4. Scale-invariant 测试推导

### 4.1 去尺度标准化

\[
z_{norm} = \frac{z-\mu_z}{\sigma_z+10^{-8}}
\]

再定义

\[
\text{mid}_{norm} = P\left(|\sigma(z_{norm})-0.5|\le\varepsilon\right)
\]

若 `mid_norm` 仍在不同结构间显著变化，则说明不仅是 scale（`sigma`）决定，结构仍有贡献。

### 4.2 相关性判据

实现中比较：

- `corr(mid_raw, 1/sigma)`
- `corr(mid_norm, 1/sigma)`

并用阈值 `|corr(mid_norm,1/sigma)| < 0.2` 给出“结构主导”的启发式判断。

---

## 5. `mid * sigma` 与 rank 的扩展关系

你提出的检验关系：

\[
\text{mid} \approx \frac{\varepsilon}{\sigma}\,\sqrt{r}
\quad\Longleftrightarrow\quad
\text{mid}\cdot\sigma \approx \varepsilon\sqrt{r}
\]

对应代码字段：

- `mid_sigma = mid_raw * sigma`
- `sqrt_r = sqrt(r)`

并绘图拟合：`mid_sigma_vs_sqrt_r.png`。

---

## 6. α 标度律（FIG7 / FIG8 / FIG9）

### 6.1 全局 α（Figure 7）

对全数据拟合：

\[
\log(\text{mid}\cdot\sigma)=\alpha\log r + b
\]

斜率即 `alpha`，并计算拟合优度 `R^2`。

### 6.2 α vs depth（Figure 8）

按 `depth` 分组重复上式拟合，得到每层深度对应 `alpha_d`。

### 6.3 α vs spectrum slope（Figure 9）

先定义谱斜率：若 `lambda_i` 为降序特征值，索引 `i=1..k`，拟合

\[
\log \lambda_i = s\log i + c
\]

则 `s` 为 spectrum slope。再分析 `alpha` 与 `s` 的关系（RMT 启发）。

---

## 7. Spectrum Sharpening Index（SSI）与风险分数

在 `analysis/spectrum_alpha_analyzer.py` 中实现：

\[
SSI = \frac{\sum_i \lambda_i^2}{(\sum_i \lambda_i)^2+10^{-8}}
\]

- `SSI` 越大，谱越尖锐（集中）
- 熵型有效秩越小，表示更接近塌缩

定义启发式风险：

\[
\text{Risk} = \frac{\mathbb{E}[SSI]}{\mathbb{E}[r_{ent}] + 10^{-8}}
\]

---

## 8. 已实现的主要图（plots/）

### 基础关系图
- `mid_vs_inv_sigma.png`
- `mid_vs_rank.png`
- `sigma_vs_depth.png`
- `rank_vs_depth.png`
- `mid_vs_predicted.png`
- `mid_heatmap_depth_width.png`

### scale-invariant / 结构图
- `mid_raw_vs_norm.png`
- `mid_norm_vs_r.png`
- `mid_norm_vs_depth.png`
- `mid_norm_vs_width.png`
- `mid_norm_vs_mid_raw.png`

### `mid*sigma` 与 α 相关图
- `mid_sigma_vs_sqrt_r.png`
- `mid_sigma_vs_r.png`
- `log_mid_sigma_vs_r.png`
- `alpha_vs_depth.png`
- `fig7_log_mid_sigma_vs_r.png`
- `fig8_alpha_vs_depth.png`
- `fig9_alpha_vs_spectrum.png`
- `alpha_vs_spectrum.png`

### 谱图
- `spectrum_d{depth}_w{width}_bn{bn}_res{res}.png`

---

## 9. 当前 `results/results.json` 的实测摘要（最新文件快照）

> 注：当前磁盘中的 `results.json` 是早期字段版本（含 `mid`，未包含 `mid_raw/mid_norm/eigvals`）。下面汇总基于该文件可直接计算的统计。

- 样本数：`N = 60`
- `sigma`：
  - mean = `11.1093`
  - min = `4.4689`
  - max = `19.1892`
- `mid`（等同早期 `mid_raw` 近似）：
  - mean = `0.004093`
  - min = `0.001000`
  - max = `0.014500`
- `r`（由 `effective_rank` 读取）：
  - mean = `8.2260`
  - min = `1.1128`
  - max = `27.9096`
- 相关性：
  - `corr(mid, 1/sigma) = 0.9209`
- 由 `mid_sigma = mid * sigma` 和 `r` 做全局 log-log 拟合：
  - `alpha = -0.1624`
  - `R^2 = 0.1174`

解释（仅基于该快照）：
- `mid` 与 `1/sigma` 强相关（符合尺度律方向）；
- `mid*sigma` 与 `r` 的单一幂律拟合目前较弱（`R^2` 较低），提示可能需要分组拟合（按 depth / width / bn-res）或使用更新后的含 `eigvals` 数据重跑。

---

## 10. 从代码到推断的整体链路

1. 训练多组 MLP（width/depth/bn/res）得到 `z,h`。  
2. 用 `z` 得到 `mid_raw`、`sigma`、`mid_sigma`；用 `h` 得到 `Cov(h)`、`eigvals`、`r`。  
3. 做三类验证：
   - 尺度验证：`mid` vs `1/sigma`；
   - 结构验证：`mid_norm` 是否仍变化、`mid_sigma` 与 `r` 的关系；
   - 谱验证：`alpha` 与 spectrum slope 的耦合。  
4. 用 `SSI` 与有效秩给出 collapse 风险指标。

---

## 11. 推荐下一步（可选）

- 用当前最新版代码重跑一次完整 sweep（保证 `results.json` 含 `mid_raw/mid_norm/eigvals` 最新字段）；
- 对 `alpha` 做分组回归（depth / width / bn-res）并报告置信区间；
- 对 Figure 9 使用“局部 α”而非“全局常数 α”，提高谱斜率相关分析的信息量。

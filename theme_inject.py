"""PHL dashboard theme — CSS string only; injected via st.markdown in app.py."""

PHL_THEME_CSS = """
<style>
  :root {
    --phl-bg: #0a0a0a;
    --phl-surface: rgba(18, 20, 28, 0.92);
    --phl-surface-2: rgba(14, 16, 22, 0.95);
    --phl-border: rgba(0, 229, 204, 0.18);
    --phl-border-soft: rgba(167, 139, 250, 0.14);
    --phl-cyan: #00e5cc;
    --phl-cyan-dim: #00d4ff;
    --phl-violet: #a78bfa;
    --phl-text: #e8ecf1;
    --phl-muted: #94a3b8;
    --phl-radius: 12px;
    --phl-shadow: 0 10px 30px -10px rgba(0, 229, 204, 0.15);
    --phl-shadow-hover: 0 18px 40px -12px rgba(0, 212, 255, 0.22);
  }

  /* App shell */
  [data-testid="stAppViewContainer"] {
    background-color: var(--phl-bg) !important;
    background-image:
      radial-gradient(ellipse 120% 80% at 50% -20%, rgba(0, 212, 255, 0.08), transparent 55%),
      linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
    background-size: auto, 40px 40px, 40px 40px;
    color: var(--phl-text);
    font-family: "Inter", "SF Pro Text", "SF Pro Display", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }

  [data-testid="stHeader"] {
    background: rgba(10, 10, 12, 0.85);
    border-bottom: 1px solid rgba(0, 229, 204, 0.08);
    backdrop-filter: blur(10px);
  }

  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(16, 18, 26, 0.98), rgba(10, 10, 14, 0.99));
    border-right: 1px solid rgba(167, 139, 250, 0.12);
  }

  [data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
  }

  section.main > div.block-container {
    padding-top: 1.25rem;
    padding-bottom: 3rem;
    max-width: 1200px;
  }

  /* Typography */
  section.main h1, section.main h2, section.main h3 {
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--phl-text) !important;
  }

  section.main p, section.main li, section.main span {
    color: var(--phl-muted);
  }

  /* Hero */
  .phl-hero {
    margin: 0 0 1.75rem 0;
    padding: 1.5rem 1.25rem 1.75rem;
    border-radius: var(--phl-radius);
    border: 1px solid rgba(0, 229, 204, 0.12);
    background: linear-gradient(135deg, rgba(20, 24, 32, 0.9), rgba(12, 14, 20, 0.95));
    box-shadow: var(--phl-shadow);
  }

  .phl-hero-title {
    margin: 0 0 0.65rem 0;
    font-size: clamp(1.65rem, 4vw, 2.35rem);
    font-weight: 600;
    line-height: 1.15;
    letter-spacing: -0.03em;
    background: linear-gradient(105deg, #f8fafc 0%, var(--phl-cyan) 45%, var(--phl-cyan-dim) 70%, var(--phl-violet) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 28px rgba(0, 229, 204, 0.18));
  }

  .phl-hero-caption {
    margin: 0;
    font-size: 0.98rem;
    line-height: 1.55;
    color: var(--phl-muted) !important;
    max-width: 52rem;
  }

  .phl-hero-caption .phl-hero-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.35em;
    height: 1.35em;
    margin-right: 0.35em;
    border-radius: 6px;
    font-size: 0.85em;
    vertical-align: middle;
    color: var(--phl-cyan);
    background: rgba(0, 229, 204, 0.08);
    border: 1px solid rgba(0, 229, 204, 0.25);
  }

  /* Section headings */
  .phl-section-h2 {
    margin: 1.5rem 0 1rem;
    font-size: 1.2rem;
    font-weight: 600;
    color: #f1f5f9 !important;
    letter-spacing: -0.02em;
  }

  .phl-section-h2::after {
    content: "";
    display: block;
    width: 48px;
    height: 2px;
    margin-top: 0.5rem;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--phl-cyan), var(--phl-violet));
    opacity: 0.85;
  }

  .phl-h3 {
    margin: 1rem 0 0.5rem;
    font-size: 1.05rem;
    font-weight: 600;
    color: #f8fafc !important;
  }

  /* Mode column cards (:has marker) */
  div[data-testid="column"]:has(.phl-mode-personal),
  div[data-testid="column"]:has(.phl-mode-pro) {
    position: relative;
    border-radius: var(--phl-radius);
    padding: 1.1rem 1.2rem 1.35rem !important;
    background: linear-gradient(160deg, rgba(22, 26, 34, 0.95), rgba(12, 14, 20, 0.98));
    border: 1px solid rgba(0, 229, 204, 0.2);
    box-shadow: var(--phl-shadow);
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
  }

  div[data-testid="column"]:has(.phl-mode-pro) {
    border-color: rgba(167, 139, 250, 0.22);
    box-shadow: 0 10px 30px -10px rgba(167, 139, 250, 0.14);
  }

  div[data-testid="column"]:has(.phl-mode-personal):hover,
  div[data-testid="column"]:has(.phl-mode-pro):hover {
    transform: translateY(-4px);
    box-shadow: var(--phl-shadow-hover);
    border-color: rgba(0, 229, 204, 0.35);
  }

  div[data-testid="column"]:has(.phl-mode-pro):hover {
    border-color: rgba(167, 139, 250, 0.38);
  }

  .phl-mode-marker {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
  }

  /* Subhead inside mode cards */
  div[data-testid="column"]:has(.phl-mode-personal) h3,
  div[data-testid="column"]:has(.phl-mode-pro) h3 {
    color: #f8fafc !important;
    font-size: 1.08rem !important;
    margin-top: 0.15rem !important;
  }

  div[data-testid="column"]:has(.phl-mode-personal) p,
  div[data-testid="column"]:has(.phl-mode-pro) p {
    color: #a8b4c4 !important;
    font-size: 0.92rem !important;
  }

  /* Buttons */
  .stButton > button {
    width: 100%;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em;
    padding: 0.65rem 1rem !important;
    border: 1px solid rgba(0, 229, 204, 0.35) !important;
    background: linear-gradient(145deg, rgba(0, 229, 204, 0.18), rgba(0, 212, 255, 0.08)) !important;
    color: #ecfeff !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease !important;
  }

  .stButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.08);
    box-shadow: 0 8px 24px rgba(0, 229, 204, 0.2);
  }

  .stButton > button:active {
    transform: translateY(0);
  }

  /* Inputs */
  div[data-baseweb="input"] input,
  div[data-baseweb="select"] > div,
  [data-testid="stNumberInput"] input {
    border-radius: 8px !important;
    background: rgba(10, 12, 18, 0.85) !important;
    color: var(--phl-text) !important;
    border-color: rgba(0, 229, 204, 0.15) !important;
  }

  [data-testid="stSlider"] .st-bc {
    background: rgba(0, 229, 204, 0.25);
  }

  /* Alerts / info */
  div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid rgba(0, 229, 204, 0.12) !important;
    background: rgba(16, 20, 28, 0.85) !important;
  }

  /* Bordered Streamlit container (Result / workbench sections) */
  [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: var(--phl-radius) !important;
    border-color: rgba(0, 212, 255, 0.18) !important;
    background: linear-gradient(165deg, rgba(20, 24, 32, 0.55), rgba(10, 12, 18, 0.75)) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), var(--phl-shadow) !important;
  }

  /* Result & structural panels */
  .phl-panel {
    margin: 1rem 0 1.25rem;
    padding: 1.15rem 1.25rem 1.25rem;
    border-radius: var(--phl-radius);
    border: 1px solid rgba(0, 212, 255, 0.14);
    background: linear-gradient(165deg, rgba(20, 24, 32, 0.88), rgba(10, 12, 18, 0.94));
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), var(--phl-shadow);
  }

  .phl-panel-title {
    margin: 0 0 0.75rem;
    font-size: 1.15rem;
    font-weight: 600;
    color: #f8fafc !important;
  }

  /* Metrics */
  [data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(24, 28, 38, 0.95), rgba(14, 16, 22, 0.98));
    border: 1px solid rgba(167, 139, 250, 0.15);
    border-radius: 10px;
    padding: 0.85rem 1rem !important;
    box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.45);
  }

  [data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  [data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--phl-cyan) !important;
    font-weight: 600 !important;
    font-size: 1.65rem !important;
  }

  [data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-weight: 500 !important;
  }

  /* Quote cards */
  .phl-quote {
    margin: 1.25rem 0 1.5rem;
    padding: 1.25rem 1.35rem 1.25rem 1.5rem;
    border-radius: var(--phl-radius);
    background: rgba(14, 16, 22, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-left: 4px solid var(--phl-cyan);
    box-shadow: var(--phl-shadow);
  }

  .phl-quote.violet {
    border-left-color: var(--phl-violet);
  }

  .phl-quote p {
    margin: 0 0 0.85rem 0;
    line-height: 1.65;
    color: #cbd5e1 !important;
    font-size: 0.98rem;
  }

  .phl-quote p:last-child {
    margin-bottom: 0;
  }

  /* Spectrum card */
  .phl-spectrum-panel {
    margin: 0 0 0.65rem 0;
    padding: 1rem 1.15rem;
    border-radius: var(--phl-radius);
    border: 1px solid rgba(0, 212, 255, 0.16);
    background: rgba(16, 20, 28, 0.75);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
  }

  .phl-spectrum-panel-head {
    font-size: 1.05rem;
    font-weight: 600;
    color: #f1f5f9 !important;
    margin-bottom: 0.45rem;
  }

  .phl-spectrum-panel-desc {
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.55;
    color: var(--phl-muted) !important;
  }

  .phl-spectrum-foot {
    margin-top: 0.35rem;
    padding: 0.85rem 1rem;
    border-radius: 10px;
    border: 1px solid rgba(167, 139, 250, 0.12);
    background: rgba(12, 14, 20, 0.55);
  }

  .phl-spectrum-chart-wrap + div [data-testid="stPlotlyChart"],
  .phl-spectrum-panel + div [data-testid="stPlotlyChart"] {
    border-radius: 10px;
    border: 1px solid rgba(0, 229, 204, 0.12);
    overflow: hidden;
    background: rgba(8, 10, 14, 0.6);
  }

  /* Tabs */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0.25rem;
    background: rgba(12, 14, 20, 0.6);
    border-radius: 10px;
    padding: 0.25rem;
    border: 1px solid rgba(255, 255, 255, 0.06);
  }

  [data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 8px;
    color: var(--phl-muted);
    font-weight: 500;
  }

  [data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0, 229, 204, 0.2), rgba(167, 139, 250, 0.12)) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(0, 229, 204, 0.25);
  }

  /* Footer */
  .phl-footer {
    margin-top: 2.5rem;
    padding: 1.5rem 1.25rem 2rem;
    border-top: 1px solid rgba(0, 229, 204, 0.1);
    border-radius: 0 0 var(--phl-radius) var(--phl-radius);
    background: linear-gradient(180deg, transparent, rgba(16, 20, 28, 0.5));
  }

  .phl-footer h3 {
    margin: 0 0 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: #e2e8f0 !important;
  }

  .phl-footer p {
    margin: 0 0 0.35rem;
    color: var(--phl-muted) !important;
    font-size: 0.92rem;
  }

  .phl-footer a {
    color: var(--phl-cyan) !important;
    text-decoration: none;
    font-weight: 500;
    border-bottom: 1px solid rgba(0, 229, 204, 0.35);
    transition: color 0.15s ease, border-color 0.15s ease;
  }

  .phl-footer a:hover {
    color: var(--phl-cyan-dim) !important;
    border-bottom-color: var(--phl-violet);
  }

  hr {
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    margin: 1.75rem 0;
  }

  /* Horizontal rule from st.markdown('---') */
  div[data-testid="stMarkdownContainer"] hr {
    margin: 1.5rem 0;
  }

  /* Dividers */
  [data-testid="stHorizontalBlock"] {
    align-items: stretch;
  }

  @media (max-width: 768px) {
    div[data-testid="column"]:has(.phl-mode-personal),
    div[data-testid="column"]:has(.phl-mode-pro) {
      margin-bottom: 1rem;
    }
    .phl-hero {
      padding: 1.1rem 1rem;
    }
  }
</style>
"""


def inject_phl_theme() -> None:
    st.markdown(PHL_THEME_CSS, unsafe_allow_html=True)

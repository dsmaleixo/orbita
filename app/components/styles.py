"""Global CSS injection for the Órbita modern UI — dark sidebar, light content."""
from __future__ import annotations

ORBITA_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root variables ───────────────────────────────────────────────────────── */
:root {
    --bg-primary: #f8fafc;
    --bg-card: #ffffff;
    --bg-card-hover: #f8fafc;
    --border: #e2e8f0;
    --border-light: #f1f5f9;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --accent: #6366f1;
    --accent-light: #818cf8;
    --accent-dark: #4f46e5;
    --accent-glow: rgba(99,102,241,0.15);
    --success: #10b981;
    --success-light: rgba(16,185,129,0.1);
    --danger: #ef4444;
    --danger-light: rgba(239,68,68,0.1);
    --warning: #f59e0b;
    --warning-light: rgba(245,158,11,0.1);
    --info: #3b82f6;
    --info-light: rgba(59,130,246,0.1);
    --radius: 14px;
    --radius-sm: 10px;
    --radius-xs: 6px;
    --shadow-xs: 0 1px 2px rgba(0,0,0,0.04);
    --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.03);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.03);
    --shadow-lg: 0 8px 30px rgba(0,0,0,0.08), 0 4px 8px rgba(0,0,0,0.04);
    --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);

    /* Dark sidebar */
    --sidebar-bg: #0f172a;
    --sidebar-hover: rgba(255,255,255,0.06);
    --sidebar-active: rgba(99,102,241,0.15);
    --sidebar-text: #cbd5e1;
    --sidebar-text-muted: #64748b;
    --sidebar-border: rgba(255,255,255,0.06);
}

/* ── Font: target layout elements only ────────────────────────────────────── */
body, .stApp, .main, p, h1, h2, h3, h4, h5, h6,
input, textarea, button, select, label,
[data-testid="stMarkdown"], [data-testid="stText"],
[class*="stButton"], [class*="stTextInput"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── App background ───────────────────────────────────────────────────────── */
.stApp {
    background-color: var(--bg-primary) !important;
}

/* ── Main content area ────────────────────────────────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar — dark theme ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-border) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1rem 0.75rem !important;
}
/* Sidebar collapse button — style for dark sidebar */
[data-testid="stSidebarCollapseButton"] svg {
    stroke: var(--sidebar-text-muted) !important;
}

/* ── Hide Streamlit chrome ────────────────────────────────────────────────── */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Typography ───────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}
h2 { font-size: 1.5rem !important; }
.stMarkdown p { color: var(--text-secondary); line-height: 1.6; }

/* ── Page header pattern ──────────────────────────────────────────────────── */
.page-header {
    margin-bottom: 2rem;
}
.page-header h2 {
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.25rem !important;
    letter-spacing: -0.03em !important;
}
.page-subtitle {
    font-size: 0.88rem;
    color: var(--text-muted);
    margin-top: -0.25rem;
}

/* ── Sidebar navigation (st.navigation) ──────────────────────────────────── */
/* Section separator / group label */
[data-testid="stSidebarNavSeparator"],
[data-testid="stSidebarNavSeparator"] * {
    color: var(--sidebar-text-muted) !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    padding: 1rem 0.75rem 0.25rem !important;
}

/* Nav link items */
[data-testid="stSidebarNavLink"] {
    border-radius: var(--radius-sm) !important;
    margin: 1px 0.25rem !important;
    padding: 0.55rem 0.85rem !important;
    transition: all var(--transition-fast) !important;
    text-decoration: none !important;
}
/* Nav link text */
[data-testid="stSidebarNavLink"] span:not([class*="material"]) {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--sidebar-text) !important;
    transition: color var(--transition-fast) !important;
}
/* Nav link icons */
[data-testid="stSidebarNavLink"] span[class*="material"] {
    font-size: 1.1rem !important;
    color: var(--sidebar-text-muted) !important;
    vertical-align: middle !important;
    transition: color var(--transition-fast) !important;
}
/* Hover state */
[data-testid="stSidebarNavLink"]:hover {
    background: var(--sidebar-hover) !important;
}
[data-testid="stSidebarNavLink"]:hover span:not([class*="material"]) {
    color: #ffffff !important;
}
[data-testid="stSidebarNavLink"]:hover span[class*="material"] {
    color: var(--accent-light) !important;
}
/* Active / selected state */
[data-testid="stSidebarNavLink"][aria-selected="true"] {
    background: var(--sidebar-active) !important;
    border-left: 3px solid var(--accent) !important;
}
[data-testid="stSidebarNavLink"][aria-selected="true"] span:not([class*="material"]) {
    color: #ffffff !important;
    font-weight: 600 !important;
}
[data-testid="stSidebarNavLink"][aria-selected="true"] span[class*="material"] {
    color: var(--accent-light) !important;
}

/* ── Metric cards ─────────────────────────────────────────────────────────── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    transition: all var(--transition);
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent-light));
    opacity: 0;
    transition: opacity var(--transition);
}
.metric-card:hover {
    border-color: rgba(99,102,241,0.3);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}
.metric-card:hover::before {
    opacity: 1;
}
.metric-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    margin-bottom: 0.75rem;
}
.metric-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-size: 1.65rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.metric-delta {
    font-size: 0.78rem;
    font-weight: 500;
    margin-top: 0.4rem;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
}
.metric-delta.positive { color: #059669; background: var(--success-light); }
.metric-delta.negative { color: #dc2626; background: var(--danger-light); }
.metric-delta.neutral  { color: var(--text-muted); background: rgba(100,116,139,0.08); }

/* ── Section headers ──────────────────────────────────────────────────────── */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--border-light);
    letter-spacing: -0.01em;
}

/* ── Row cards (transaction, recurring, etc.) ─────────────────────────────── */
.row-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.1rem;
    background: var(--bg-card);
    border-radius: var(--radius-sm);
    margin-bottom: 0.35rem;
    border: 1px solid var(--border);
    transition: all var(--transition-fast);
}
.row-card:hover {
    border-color: rgba(99,102,241,0.2);
    box-shadow: var(--shadow);
    transform: translateX(2px);
}
.row-card-left {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    flex: 1;
    min-width: 0;
}
.row-card-icon {
    width: 38px;
    height: 38px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.row-card-title {
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.row-card-sub {
    font-size: 0.74rem;
    color: var(--text-muted);
    margin-top: 1px;
}
.row-card-amount {
    font-size: 0.95rem;
    font-weight: 700;
    white-space: nowrap;
    margin-left: 1rem;
    flex-shrink: 0;
}

/* ── Data tables ──────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-card) !important;
}
[data-testid="stDataFrame"] th {
    background-color: var(--bg-primary) !important;
    color: var(--text-secondary) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stDataFrame"] td {
    color: var(--text-primary) !important;
    font-size: 0.85rem !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {
    background-color: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1.3rem !important;
    transition: all var(--transition) !important;
    box-shadow: 0 1px 3px rgba(99,102,241,0.25) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background-color: var(--accent-dark) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}
.stButton > button[kind="secondary"] {
    background-color: white !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    box-shadow: var(--shadow-xs) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(99,102,241,0.04) !important;
}

/* ── Inputs & selects ─────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stNumberInput > div > div > input {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    transition: all var(--transition-fast) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* ── Chat messages ────────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background-color: var(--bg-card) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    margin-bottom: 0.75rem !important;
    box-shadow: var(--shadow-xs) !important;
}
[data-testid="stChatInput"] > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    transition: border-color var(--transition-fast) !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 2px solid var(--border-light) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 0 !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.65rem 1.3rem !important;
    transition: all var(--transition-fast) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--accent) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    font-weight: 600 !important;
}

/* ── Expanders ────────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background-color: var(--bg-card) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    border: 1px solid var(--border) !important;
    transition: all var(--transition-fast) !important;
}
.streamlit-expanderHeader:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
.streamlit-expanderContent {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* ── Alerts — ensure readability ──────────────────────────────────────────── */
.stAlert {
    border-radius: var(--radius-sm) !important;
    box-shadow: var(--shadow-xs) !important;
}
.stAlert [data-testid="stMarkdownContainer"],
.stAlert [data-testid="stMarkdownContainer"] p,
.stAlert [data-testid="stMarkdownContainer"] a,
.stAlert [data-testid="stMarkdownContainer"] strong,
.stAlert [data-testid="stMarkdownContainer"] code {
    color: inherit !important;
}
/* Warning alert */
[data-testid="stAlert"][data-baseweb="notification"] {
    background-color: #fffbeb !important;
    border: 1px solid #fde68a !important;
    color: #92400e !important;
}
/* Info alert */
div[data-testid="stAlert"]:has([data-testid*="info"]),
div[role="alert"] {
    color: #1e3a5f !important;
}
/* Ensure all st.warning/st.info/st.error/st.success text is readable */
.stAlert div, .stAlert p, .stAlert span:not([class*="material"]) {
    color: inherit !important;
}
.stAlert a {
    color: #2563eb !important;
    text-decoration: underline !important;
}
.stAlert code {
    background: rgba(0,0,0,0.06) !important;
    color: inherit !important;
    padding: 0.1rem 0.35rem !important;
    border-radius: 4px !important;
    font-size: 0.85em !important;
}

/* ── Badge / chip ─────────────────────────────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    font-family: 'Inter', sans-serif;
    transition: all var(--transition-fast);
}
.badge-success { background: var(--success-light); color: #059669 !important; }
.badge-danger  { background: var(--danger-light); color: #dc2626 !important; }
.badge-warning { background: var(--warning-light); color: #d97706 !important; }
.badge-info    { background: var(--info-light); color: #2563eb !important; }
.badge-neutral { background: rgba(100,116,139,0.08); color: #475569 !important; }

/* ── Skeleton loader ──────────────────────────────────────────────────────── */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
.skeleton {
    background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s ease-in-out infinite;
    border-radius: var(--radius-sm);
}
.skeleton-card {
    height: 100px;
    border-radius: var(--radius);
    margin-bottom: 0.75rem;
}
.skeleton-line {
    height: 14px;
    margin-bottom: 0.5rem;
    width: 100%;
}
.skeleton-line-short { width: 60%; }
.skeleton-line-xs { width: 40%; }

/* ── Category dots ────────────────────────────────────────────────────────── */
.cat-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

/* ── Divider ──────────────────────────────────────────────────────────────── */
.stDivider { border-color: var(--border-light) !important; }

/* ── Progress bar ─────────────────────────────────────────────────────────── */
.stProgress > div > div {
    background-color: var(--accent) !important;
    border-radius: 999px !important;
}
.stProgress > div {
    background-color: var(--border) !important;
    border-radius: 999px !important;
}

/* ── Sidebar logo area ────────────────────────────────────────────────────── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 0.85rem 1.25rem;
    border-bottom: 1px solid var(--sidebar-border);
    margin-bottom: 0.5rem;
}
.sidebar-logo-icon {
    font-size: 1.75rem;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--accent), var(--accent-light));
    border-radius: var(--radius-sm);
}
.sidebar-logo-text {
    font-size: 1.2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.03em;
    font-family: 'Inter', sans-serif;
}
.sidebar-logo-sub {
    font-size: 0.68rem;
    color: var(--sidebar-text-muted);
    margin-top: -2px;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.02em;
}

/* ── Sidebar footer ───────────────────────────────────────────────────────── */
.sidebar-footer {
    font-size: 0.72rem;
    color: var(--sidebar-text-muted);
    padding: 0.75rem 0.85rem;
    line-height: 1.9;
    border-top: 1px solid var(--sidebar-border);
}
.sidebar-footer .status-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}
.sidebar-footer .status-dot.live { background: #10b981; box-shadow: 0 0 6px rgba(16,185,129,0.5); }
.sidebar-footer .status-dot.demo { background: #f59e0b; box-shadow: 0 0 6px rgba(245,158,11,0.3); }
.sidebar-footer .status-dot.off { background: #64748b; }

/* ── Sidebar divider override ─────────────────────────────────────────────── */
[data-testid="stSidebar"] hr {
    border-color: var(--sidebar-border) !important;
}

/* ── Hero card (gradient) ─────────────────────────────────────────────────── */
.hero-card {
    background: linear-gradient(135deg, #4338ca, #6366f1, #818cf8);
    border-radius: 18px;
    padding: 2rem 2.25rem;
    margin-bottom: 1.75rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.25), 0 0 0 1px rgba(255,255,255,0.1) inset;
    position: relative;
    overflow: hidden;
}
.hero-card::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-card-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: rgba(255,255,255,0.65);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.hero-card-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0.3rem 0;
    letter-spacing: -0.03em;
}
.hero-card-sub {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.55);
}

/* ── Monthly breakdown row ────────────────────────────────────────────────── */
.month-row {
    padding: 0.9rem 1.1rem;
    background: var(--bg-card);
    border-radius: var(--radius-sm);
    margin-bottom: 0.4rem;
    border: 1px solid var(--border);
    transition: all var(--transition-fast);
}
.month-row:hover {
    border-color: rgba(99,102,241,0.2);
    box-shadow: var(--shadow);
}

/* ── Card elevation helper ────────────────────────────────────────────────── */
.card-elevated {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow);
    transition: all var(--transition);
}
.card-elevated:hover {
    box-shadow: var(--shadow-md);
    border-color: rgba(99,102,241,0.15);
}

/* ── Smooth fade-in ───────────────────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeInUp 0.3s ease-out;
}
</style>
"""


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#475569", size=12),
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#e2e8f0",
        borderwidth=1,
        font=dict(size=11, color="#475569"),
    ),
    xaxis=dict(
        gridcolor="#f1f5f9",
        linecolor="#e2e8f0",
        tickfont=dict(size=11, color="#94a3b8"),
        showgrid=True,
    ),
    yaxis=dict(
        gridcolor="#f1f5f9",
        linecolor="#e2e8f0",
        tickfont=dict(size=11, color="#94a3b8"),
        showgrid=True,
    ),
)

# Color palette for charts
CHART_COLORS = [
    "#6366f1", "#10b981", "#f59e0b", "#ef4444", "#3b82f6",
    "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16", "#f97316",
]

CATEGORY_COLORS = {
    "alimentacao": "#f59e0b",
    "transporte": "#3b82f6",
    "moradia": "#6366f1",
    "saude": "#10b981",
    "lazer": "#ec4899",
    "educacao": "#8b5cf6",
    "vestuario": "#f97316",
    "investimentos": "#06b6d4",
    "receita": "#10b981",
    "outros": "#64748b",
}

CATEGORY_EMOJI = {
    "alimentacao": "🍽️",
    "transporte": "🚗",
    "moradia": "🏠",
    "saude": "💊",
    "lazer": "🎉",
    "educacao": "📚",
    "vestuario": "👕",
    "investimentos": "📈",
    "receita": "💰",
    "outros": "📦",
}


def inject_css() -> None:
    """Inject the global CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(ORBITA_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    """Render a consistent page header."""
    import streamlit as st
    st.markdown(f"""
    <div class="page-header fade-in">
        <h2>{title}</h2>
        <div class="page-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def card(content_html: str) -> None:
    """Render an HTML card block."""
    import streamlit as st
    st.markdown(f'<div class="card-elevated fade-in">{content_html}</div>', unsafe_allow_html=True)


def metric_card(
    label: str,
    value: str,
    delta: str = "",
    delta_type: str = "neutral",
    icon: str = "",
    icon_bg: str = "rgba(99,102,241,0.1)",
) -> None:
    """Render a KPI metric card with optional icon."""
    import streamlit as st
    icon_html = ""
    if icon:
        icon_html = f'<div class="metric-icon" style="background:{icon_bg};">{icon}</div>'
    delta_html = f'<div class="metric-delta {delta_type}">{delta}</div>' if delta else ""
    html = f"""
    <div class="metric-card fade-in">
        {icon_html}
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def hero_card(label: str, value: str, subtitle: str = "") -> None:
    """Render a gradient hero/highlight card."""
    import streamlit as st
    sub_html = f'<div class="hero-card-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="hero-card fade-in">
        <div class="hero-card-label">{label}</div>
        <div class="hero-card-value">{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def section_title(text: str) -> None:
    import streamlit as st
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def skeleton_cards(count: int = 4) -> None:
    """Render skeleton loading placeholders."""
    import streamlit as st
    cols = st.columns(count)
    for i in range(count):
        with cols[i]:
            st.markdown("""
            <div class="skeleton skeleton-card"></div>
            """, unsafe_allow_html=True)


def skeleton_rows(count: int = 5) -> None:
    """Render skeleton rows for list loading."""
    import streamlit as st
    for _ in range(count):
        st.markdown("""
        <div class="skeleton skeleton-line" style="height:52px;margin-bottom:0.4rem;border-radius:10px;"></div>
        """, unsafe_allow_html=True)


def row_card(
    title: str,
    subtitle: str,
    amount_str: str,
    amount_color: str,
    icon: str = "📦",
    icon_bg: str = "rgba(99,102,241,0.1)",
    extra_right: str = "",
) -> None:
    """Render a standardized row card for transactions, recurring, etc."""
    import streamlit as st
    extra_html = f'<div style="font-size:0.72rem;color:#94a3b8;margin-top:1px;">{extra_right}</div>' if extra_right else ""
    st.markdown(f"""
    <div class="row-card fade-in">
        <div class="row-card-left">
            <div class="row-card-icon" style="background:{icon_bg};">{icon}</div>
            <div style="min-width:0;flex:1;">
                <div class="row-card-title">{title}</div>
                <div class="row-card-sub">{subtitle}</div>
            </div>
        </div>
        <div style="text-align:right;flex-shrink:0;margin-left:1rem;">
            <div class="row-card-amount" style="color:{amount_color};">{amount_str}</div>
            {extra_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

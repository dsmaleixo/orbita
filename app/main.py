"""Órbita — Personal Finance App entry point.

Run with:
    uv run streamlit run app/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Órbita",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.components.styles import inject_css
inject_css()


def _init_graph() -> None:
    if "graph" not in st.session_state:
        with st.spinner("Inicializando assistente..."):
            try:
                from src.graph.builder import build_graph
                st.session_state.graph = build_graph()
            except Exception:
                st.session_state.graph = None


def _render_sidebar_logo() -> None:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🪐</div>
        <div>
            <div class="sidebar-logo-text">Órbita</div>
            <div class="sidebar-logo-sub">Finanças Pessoais</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_sidebar_footer() -> None:
    from src.config import settings
    is_mock = settings.MCP_MOCK
    connected = bool(settings.PLUGGY_ITEM_ID)

    if is_mock:
        dot_class, status_label = "demo", "Demo (mock)"
    elif connected:
        dot_class, status_label = "live", "Open Finance"
    else:
        dot_class, status_label = "off", "Desconectado"

    conn_label = "Conectado" if connected else "Desconectado"
    conn_dot = "live" if connected else "off"

    st.markdown(f"""
    <div class="sidebar-footer">
        <div><span class="status-dot {dot_class}"></span>{status_label}</div>
        <div><span class="status-dot {conn_dot}"></span>{conn_label}</div>
        <div style="color:#818cf8;">⚙ {settings.OLLAMA_MODEL}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Page imports ───────────────────────────────────────────────────────────────

from app.pages.dashboard import render_dashboard
from app.pages.transactions import render_transactions
from app.pages.cash_flow import render_cash_flow
from app.pages.accounts import render_accounts
from app.pages.assets import render_assets
from app.pages.recurring import render_recurring
from app.pages.categories import render_categories
from app.pages.goals import render_goals_page
from app.pages.reports import render_reports_page
from app.pages.chat import render_chat_page
from app.pages.connect import render_connect_page


def main() -> None:
    _init_graph()

    with st.sidebar:
        _render_sidebar_logo()

    pg = st.navigation(
        {
            "Visão Geral": [
                st.Page(render_dashboard,    title="Dashboard",       icon=":material/space_dashboard:"),
            ],
            "Finanças": [
                st.Page(render_transactions, title="Transações",      icon=":material/receipt_long:"),
                st.Page(render_cash_flow,    title="Fluxo de Caixa",  icon=":material/waterfall_chart:"),
                st.Page(render_accounts,     title="Contas",          icon=":material/account_balance:"),
                st.Page(render_assets,       title="Patrimônio",      icon=":material/savings:"),
                st.Page(render_recurring,    title="Recorrentes",     icon=":material/event_repeat:"),
                st.Page(render_categories,   title="Categorias",      icon=":material/donut_small:"),
                st.Page(render_goals_page,   title="Metas",           icon=":material/flag:"),
                st.Page(render_reports_page, title="Relatórios",      icon=":material/assessment:"),
            ],
            "Assistente": [
                st.Page(render_chat_page,    title="Assistente IA",   icon=":material/smart_toy:"),
            ],
            "Configurações": [
                st.Page(render_connect_page, title="Conectar Banco",  icon=":material/link:"),
            ],
        },
        expanded=True,
    )

    with st.sidebar:
        st.markdown("---")
        _render_sidebar_footer()

    pg.run()


if __name__ == "__main__":
    main()

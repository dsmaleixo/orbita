"""Cash flow page — income vs expenses over time."""
from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from app.components.styles import metric_card, page_header, section_title, skeleton_cards
from app.components.charts import area_chart_cashflow, bar_chart_income_expense
from app.data_layer import fetch_transactions, get_monthly_data, get_summary


def render_cash_flow() -> None:
    page_header("Fluxo de Caixa", "Análise de entradas e saídas no período")

    # Period selector
    col1, _, _ = st.columns([2, 3, 1])
    with col1:
        months = st.slider("Meses de histórico", 1, 12, 6)

    today = datetime.today()
    start = (today - timedelta(days=months * 30)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")

    loading = st.empty()
    with loading.container():
        skeleton_cards(3)

    txns = fetch_transactions(start, end)
    loading.empty()

    summary = get_summary(txns)
    monthly = get_monthly_data(txns, months=months)

    # ── KPI row ────────────────────────────────────────────────────────────
    savings_rate = (summary["net"] / summary["income"] * 100) if summary["income"] > 0 else 0
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card(
            "Total Receitas", f"R${summary['income']:,.2f}",
            delta_type="positive", icon="📈", icon_bg="rgba(16,185,129,0.1)",
        )
    with c2:
        metric_card(
            "Total Despesas", f"R${summary['expenses']:,.2f}",
            delta_type="negative", icon="📉", icon_bg="rgba(239,68,68,0.1)",
        )
    with c3:
        metric_card(
            "Taxa de Poupança", f"{savings_rate:.1f}%",
            delta="Ótimo" if savings_rate >= 20 else ("OK" if savings_rate >= 10 else "Abaixo do ideal"),
            delta_type="positive" if savings_rate >= 20 else ("neutral" if savings_rate >= 10 else "negative"),
            icon="🎯", icon_bg="rgba(99,102,241,0.1)",
        )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Monthly bar chart ──────────────────────────────────────────────────
    bar_chart_income_expense(monthly)

    # ── Cumulative cash flow ───────────────────────────────────────────────
    cumulative_data = []
    running = 0.0
    for month in monthly:
        running += month["net"]
        cumulative_data.append({"date": month["month"], "cumulative": running})
    area_chart_cashflow(cumulative_data)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Monthly breakdown ──────────────────────────────────────────────────
    section_title("Resumo Mensal")
    for m in reversed(monthly):
        net = m["net"]
        net_color = "#10b981" if net >= 0 else "#ef4444"
        bar_width = min(100, abs(m["expenses"]) / max(1, m["income"]) * 100)
        st.markdown(f"""
        <div class="month-row fade-in">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                <span style="font-weight:600;color:var(--text-primary);font-size:0.9rem;">{m['month']}</span>
                <span style="font-weight:700;color:{net_color};font-size:0.9rem;">
                    {'+'if net>=0 else ''}R${net:,.2f}
                </span>
            </div>
            <div style="display:flex;gap:1.5rem;font-size:0.8rem;">
                <span style="color:#10b981;">↑ R${m['income']:,.2f}</span>
                <span style="color:#ef4444;">↓ R${m['expenses']:,.2f}</span>
            </div>
            <div style="margin-top:0.5rem;background:var(--border);border-radius:999px;height:4px;">
                <div style="width:{bar_width:.0f}%;background:#ef4444;border-radius:999px;height:4px;
                            transition:width 0.5s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

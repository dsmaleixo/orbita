"""Dashboard overview page — KPIs, charts, recent transactions."""
from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from app.components.styles import (
    CATEGORY_COLORS, CATEGORY_EMOJI, metric_card, page_header,
    row_card, section_title, skeleton_cards, skeleton_rows,
)
from app.components.charts import bar_chart_income_expense, donut_chart_categories, line_chart_balance
from app.data_layer import (
    fetch_balances, fetch_transactions,
    get_category_totals, get_monthly_data, get_summary, get_balance_history,
)


def render_dashboard() -> None:
    page_header("Visão Geral", "Resumo financeiro do período")

    # ── Date range picker ──────────────────────────────────────────────────
    col_l, col_r = st.columns([3, 1])
    with col_r:
        period = st.selectbox(
            "Período",
            ["Este mês", "Últimos 30 dias", "Últimos 3 meses", "Últimos 6 meses"],
            label_visibility="collapsed",
        )

    today = datetime.today()
    period_days = {"Este mês": 0, "Últimos 30 dias": 30, "Últimos 3 meses": 90, "Últimos 6 meses": 180}
    if period == "Este mês":
        start = today.replace(day=1).strftime("%Y-%m-%d")
    else:
        start = (today - timedelta(days=period_days[period])).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")

    # Show skeleton while loading
    loading = st.empty()
    with loading.container():
        skeleton_cards(4)

    txns = fetch_transactions(start, end)
    balances = fetch_balances()
    loading.empty()

    summary = get_summary(txns)
    total_balance = sum(b.get("balance", 0) for b in balances)

    # ── KPI cards ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Saldo Total",
            f"R${total_balance:,.2f}",
            icon="🏦",
            icon_bg="rgba(99,102,241,0.1)",
        )
    with c2:
        metric_card(
            "Receitas",
            f"R${summary['income']:,.2f}",
            delta=f"↑ {len([t for t in txns if t['amount'] > 0])} entradas",
            delta_type="positive",
            icon="📈",
            icon_bg="rgba(16,185,129,0.1)",
        )
    with c3:
        metric_card(
            "Despesas",
            f"R${summary['expenses']:,.2f}",
            delta=f"↓ {len([t for t in txns if t['amount'] < 0])} saídas",
            delta_type="negative",
            icon="📉",
            icon_bg="rgba(239,68,68,0.1)",
        )
    with c4:
        net = summary["net"]
        metric_card(
            "Resultado",
            f"R${net:,.2f}",
            delta="Positivo" if net >= 0 else "Negativo",
            delta_type="positive" if net >= 0 else "negative",
            icon="⚡",
            icon_bg="rgba(245,158,11,0.1)",
        )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Charts row ─────────────────────────────────────────────────────────
    col1, col2 = st.columns([3, 2])
    with col1:
        monthly = get_monthly_data(txns, months=6)
        bar_chart_income_expense(monthly)
    with col2:
        cats = get_category_totals(txns)
        donut_chart_categories(cats)

    # ── Balance evolution ─────────────────────────────────────────────────
    history = get_balance_history(txns, initial_balance=total_balance - summary["net"])
    if history:
        line_chart_balance(history)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Recent transactions ────────────────────────────────────────────────
    section_title("Transações Recentes")
    recent = sorted(txns, key=lambda x: x.get("date", ""), reverse=True)[:10]

    if not recent:
        st.info("Nenhuma transação encontrada no período.")
        return

    for txn in recent:
        amount = txn.get("amount", 0)
        is_income = amount > 0
        color = "#10b981" if is_income else "#ef4444"
        sign = "+" if is_income else "-"
        cat = txn.get("category", "outros")
        emoji = "💰" if is_income else CATEGORY_EMOJI.get(cat, "📦")
        cat_color = CATEGORY_COLORS.get(cat, "#64748b")

        row_card(
            title=txn.get("description", "")[:45],
            subtitle=f"{txn.get('date', '')} · <span style='color:{cat_color}'>{cat.capitalize()}</span>",
            amount_str=f"{sign}R${abs(amount):,.2f}",
            amount_color=color,
            icon=emoji,
            icon_bg="rgba(16,185,129,0.1)" if is_income else "rgba(99,102,241,0.08)",
        )

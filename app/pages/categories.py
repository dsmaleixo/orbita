"""Expense categories page."""
from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from app.components.styles import (
    CATEGORY_COLORS, CATEGORY_EMOJI, page_header, section_title, skeleton_cards,
)
from app.components.charts import donut_chart_categories, horizontal_bar_categories
from app.data_layer import fetch_transactions, get_category_totals


def render_categories() -> None:
    page_header("Categorias de Gastos", "Onde seu dinheiro está sendo gasto")

    today = datetime.today()
    col1, _, _ = st.columns([2, 3, 1])
    with col1:
        months = st.slider("Meses", 1, 6, 1, format="%d mês(es)")

    start = (today - timedelta(days=months * 30)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")

    loading = st.empty()
    with loading.container():
        skeleton_cards(3)

    txns = fetch_transactions(start, end)
    loading.empty()

    cats = get_category_totals(txns)
    total_expenses = sum(cats.values())

    if not cats:
        st.info("Nenhuma despesa encontrada no período.")
        return

    # ── Summary chips ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;gap:0.75rem;margin-bottom:1.25rem;flex-wrap:wrap;" class="fade-in">
        <span class="badge badge-neutral">{len(cats)} categorias</span>
        <span class="badge badge-danger">Total: R${total_expenses:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────
    col1, col2 = st.columns([3, 2])
    with col1:
        horizontal_bar_categories(cats)
    with col2:
        donut_chart_categories(cats)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Category detail cards ──────────────────────────────────────────────
    section_title("Detalhamento por Categoria")
    cols = st.columns(3)
    for i, (cat, total) in enumerate(cats.items()):
        pct = total / total_expenses * 100 if total_expenses else 0
        color = CATEGORY_COLORS.get(cat, "#64748b")
        emoji = CATEGORY_EMOJI.get(cat, "📦")
        cat_txns = [t for t in txns if t.get("category") == cat and t.get("amount", 0) < 0]

        with cols[i % 3]:
            st.markdown(f"""
            <div class="card-elevated fade-in" style="margin-bottom:0.75rem;">
                <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.75rem;">
                    <span style="font-size:1.2rem;">{emoji}</span>
                    <span style="font-size:0.88rem;font-weight:600;color:var(--text-primary);">{cat.capitalize()}</span>
                </div>
                <div style="font-size:1.3rem;font-weight:800;color:{color};letter-spacing:-0.02em;">R${total:,.2f}</div>
                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;">
                    {pct:.1f}% dos gastos · {len(cat_txns)} transações
                </div>
                <div style="background:var(--border);border-radius:999px;height:4px;margin-top:0.6rem;">
                    <div style="width:{pct:.1f}%;background:{color};border-radius:999px;height:4px;
                                transition:width 0.5s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

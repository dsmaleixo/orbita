"""Transactions page — filterable, searchable transaction list."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from app.components.styles import (
    CATEGORY_COLORS, CATEGORY_EMOJI, page_header, row_card, skeleton_rows,
)
from app.data_layer import fetch_transactions


def render_transactions() -> None:
    page_header("Transações", "Histórico completo de transações")

    # ── Filters bar ────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    today = datetime.today()
    with col1:
        start = st.date_input("De", value=today.replace(day=1))
    with col2:
        end = st.date_input("Até", value=today)
    with col3:
        search = st.text_input("Buscar", placeholder="Descrição...")
    with col4:
        st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
        show_only = st.selectbox("Tipo", ["Todos", "Receitas", "Despesas"], label_visibility="collapsed")

    loading = st.empty()
    with loading.container():
        skeleton_rows(5)

    txns = fetch_transactions(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    loading.empty()

    # Apply filters
    if search:
        txns = [t for t in txns if search.lower() in t.get("description", "").lower()]
    if show_only == "Receitas":
        txns = [t for t in txns if t.get("amount", 0) > 0]
    elif show_only == "Despesas":
        txns = [t for t in txns if t.get("amount", 0) < 0]

    # Category filter
    all_cats = sorted(set(t.get("category", "outros") for t in txns))
    selected_cats = st.multiselect(
        "Categorias",
        options=all_cats,
        default=all_cats,
        label_visibility="collapsed",
    )
    if selected_cats:
        txns = [t for t in txns if t.get("category", "outros") in selected_cats]

    # ── Summary chips ──────────────────────────────────────────────────────
    income = sum(t["amount"] for t in txns if t["amount"] > 0)
    expenses = sum(abs(t["amount"]) for t in txns if t["amount"] < 0)
    st.markdown(f"""
    <div style="display:flex;gap:0.75rem;margin-bottom:1rem;flex-wrap:wrap;" class="fade-in">
        <span class="badge badge-neutral">{len(txns)} transações</span>
        <span class="badge badge-success">Receitas: R${income:,.2f}</span>
        <span class="badge badge-danger">Despesas: R${expenses:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    if not txns:
        st.info("Nenhuma transação encontrada com os filtros selecionados.")
        return

    # ── Transaction rows ───────────────────────────────────────────────────
    sorted_txns = sorted(txns, key=lambda x: x.get("date", ""), reverse=True)

    for txn in sorted_txns:
        amount = txn.get("amount", 0)
        is_income = amount > 0
        color = "#10b981" if is_income else "#ef4444"
        sign = "+" if is_income else "-"
        cat = txn.get("category", "outros")
        cat_color = CATEGORY_COLORS.get(cat, "#64748b")
        emoji = "💰" if is_income else CATEGORY_EMOJI.get(cat, "📦")

        row_card(
            title=txn.get("description", "")[:50],
            subtitle=f"{txn.get('date', '')} · <span style='color:{cat_color}'>{cat.capitalize()}</span>",
            amount_str=f"{sign}R${abs(amount):,.2f}",
            amount_color=color,
            icon=emoji,
            icon_bg="rgba(16,185,129,0.1)" if is_income else "rgba(99,102,241,0.08)",
        )

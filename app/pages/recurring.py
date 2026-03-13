"""Recurring payments page."""
from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from app.components.styles import (
    CATEGORY_COLORS, CATEGORY_EMOJI, metric_card, page_header,
    row_card, section_title, skeleton_cards, skeleton_rows,
)
from app.data_layer import fetch_transactions, get_recurring


def render_recurring() -> None:
    page_header("Pagamentos Recorrentes", "Assinaturas e cobranças periódicas detectadas automaticamente")

    today = datetime.today()
    start = (today - timedelta(days=180)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")

    loading = st.empty()
    with loading.container():
        skeleton_cards(3)
        skeleton_rows(4)

    txns = fetch_transactions(start, end)
    recurring = get_recurring(txns)
    loading.empty()

    if not recurring:
        st.info("Nenhum pagamento recorrente detectado nos últimos 6 meses.")
        return

    total_monthly = sum(r["avg_amount"] for r in recurring)

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card(
            "Recorrências", str(len(recurring)),
            icon="🔄", icon_bg="rgba(99,102,241,0.1)",
        )
    with c2:
        metric_card(
            "Custo Mensal", f"R${total_monthly:,.2f}",
            delta_type="negative",
            icon="📅", icon_bg="rgba(239,68,68,0.1)",
        )
    with c3:
        metric_card(
            "Custo Anual", f"R${total_monthly * 12:,.2f}",
            delta_type="negative",
            icon="📊", icon_bg="rgba(245,158,11,0.1)",
        )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    section_title("Detalhamento")

    for r in recurring:
        cat = r.get("category", "outros")
        cat_color = CATEGORY_COLORS.get(cat, "#64748b")
        emoji = CATEGORY_EMOJI.get(cat, "📦")
        occ = r["occurrences"]
        months = r["months"]

        row_card(
            title=r["description"][:45],
            subtitle=f"<span style='color:{cat_color}'>{cat.capitalize()}</span> · {occ}x em {months} meses · Última: {r['last_date']}",
            amount_str=f"-R${r['avg_amount']:,.2f}",
            amount_color="#ef4444",
            icon=emoji,
            icon_bg="rgba(99,102,241,0.08)",
            extra_right="por mês",
        )

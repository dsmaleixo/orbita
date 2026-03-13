"""Accounts page — balances and account details."""
from __future__ import annotations

import streamlit as st

from app.components.styles import hero_card, page_header, section_title, skeleton_cards
from app.data_layer import fetch_accounts, fetch_balances, fetch_transactions, default_date_range

ACCOUNT_TYPE_EMOJI = {
    "corrente": "🏦", "poupanca": "🐷", "investimento": "📈",
    "cartao": "💳", "cripto": "₿", "outros": "💰",
}
ACCOUNT_TYPE_LABEL = {
    "corrente": "Conta Corrente", "poupanca": "Poupança",
    "investimento": "Investimentos", "cartao": "Cartão de Crédito",
    "cripto": "Cripto", "outros": "Outros",
}


def render_accounts() -> None:
    page_header("Contas", "Suas contas vinculadas via Open Finance")

    loading = st.empty()
    with loading.container():
        skeleton_cards(3)

    balances = fetch_balances()
    accounts = fetch_accounts()
    loading.empty()

    bal_map = {b["account_id"]: b for b in balances}
    acc_map = {a["id"]: a for a in accounts}
    total = sum(b.get("balance", 0) for b in balances)

    # ── Total balance hero card ───────────────────────────────────────────
    hero_card(
        label="Patrimônio Total",
        value=f"R${total:,.2f}",
        subtitle=f"{len(balances)} conta{'s' if len(balances) != 1 else ''} vinculada{'s' if len(balances) != 1 else ''}",
    )

    # ── Account cards ────────────────────────────────────────────────────
    cols = st.columns(min(3, max(1, len(balances))))
    for i, bal in enumerate(balances):
        acc_id = bal.get("account_id", "")
        acc = acc_map.get(acc_id, {})
        acc_type = acc.get("type", "corrente").lower()
        emoji = ACCOUNT_TYPE_EMOJI.get(acc_type, "💰")
        label = ACCOUNT_TYPE_LABEL.get(acc_type, acc_type.capitalize())
        name = acc.get("name", bal.get("institution", "Conta"))
        balance = bal.get("balance", 0)
        balance_color = "#10b981" if balance >= 0 else "#ef4444"

        with cols[i % len(cols)]:
            st.markdown(f"""
            <div class="card-elevated fade-in" style="margin-bottom:0.75rem;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
                    <div style="width:42px;height:42px;background:rgba(99,102,241,0.1);
                                border-radius:var(--radius-sm);display:flex;align-items:center;
                                justify-content:center;font-size:1.2rem;">{emoji}</div>
                    <span class="badge badge-neutral">{label}</span>
                </div>
                <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:0.2rem;">{name}</div>
                <div style="font-size:1.6rem;font-weight:800;color:{balance_color};letter-spacing:-0.02em;">
                    R${balance:,.2f}
                </div>
                <div style="font-size:0.75rem;color:var(--text-secondary);margin-top:0.3rem;">
                    {acc.get('currency_code', 'BRL')}
                    {f" · ****{acc.get('last_four', '')}" if acc.get('last_four') else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Recent activity per account ──────────────────────────────────────
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    section_title("Atividade Recente por Conta")
    start, end = default_date_range()
    txns = fetch_transactions(start, end)
    for bal in balances:
        acc_id = bal.get("account_id", "")
        acc_txns = [t for t in txns if t.get("account_id") == acc_id]
        if acc_txns:
            acc = acc_map.get(acc_id, {})
            with st.expander(f"📋 {acc.get('name', acc_id)} — {len(acc_txns)} transações", expanded=False):
                for t in sorted(acc_txns, key=lambda x: x.get("date", ""), reverse=True)[:5]:
                    amt = t.get("amount", 0)
                    color = "#10b981" if amt > 0 else "#ef4444"
                    sign = "+" if amt > 0 else "-"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:0.55rem 0;
                                border-bottom:1px solid var(--border-light);">
                        <span style="font-size:0.85rem;color:var(--text-secondary);">{t.get('description','')[:35]}</span>
                        <span style="font-size:0.85rem;font-weight:600;color:{color};">{sign}R${abs(amt):,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)

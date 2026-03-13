"""Assets page — net worth tracking."""
from __future__ import annotations

import streamlit as st

from app.components.styles import page_header, section_title, skeleton_cards
from app.data_layer import fetch_balances, fetch_accounts


def render_assets() -> None:
    page_header("Patrimônio", "Visão consolidada dos seus ativos")

    loading = st.empty()
    with loading.container():
        skeleton_cards(2)

    balances = fetch_balances()
    accounts = fetch_accounts()
    loading.empty()

    acc_map = {a["id"]: a for a in accounts}

    # Group by type
    groups = {"corrente": [], "poupanca": [], "investimento": [], "outros": []}
    for bal in balances:
        acc = acc_map.get(bal.get("account_id", ""), {})
        atype = acc.get("type", "outros").lower()
        key = atype if atype in groups else "outros"
        groups[key].append({**bal, **acc})

    total = sum(b.get("balance", 0) for b in balances)

    labels = {"corrente": "Conta Corrente", "poupanca": "Poupança", "investimento": "Investimentos", "outros": "Outros"}
    emojis = {"corrente": "🏦", "poupanca": "🐷", "investimento": "📈", "outros": "💰"}
    colors = {"corrente": "#6366f1", "poupanca": "#10b981", "investimento": "#f59e0b", "outros": "#64748b"}

    c1, c2 = st.columns([2, 3])
    with c1:
        for gtype, items in groups.items():
            if not items:
                continue
            group_total = sum(i.get("balance", 0) for i in items)
            pct = group_total / total * 100 if total else 0
            st.markdown(f"""
            <div class="card-elevated fade-in" style="margin-bottom:0.6rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                    <span style="font-size:0.9rem;font-weight:600;color:var(--text-primary);">
                        {emojis[gtype]} {labels[gtype]}
                    </span>
                    <span style="font-size:0.9rem;font-weight:700;color:{colors[gtype]};">
                        R${group_total:,.2f}
                    </span>
                </div>
                <div style="background:var(--border);border-radius:999px;height:5px;">
                    <div style="width:{pct:.1f}%;background:{colors[gtype]};border-radius:999px;height:5px;
                                transition:width 0.5s ease;"></div>
                </div>
                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:0.3rem;">{pct:.1f}% do patrimônio</div>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        import plotly.graph_objects as go
        from app.components.styles import PLOTLY_LAYOUT
        gdata = {labels[k]: sum(i.get("balance", 0) for i in v) for k, v in groups.items() if v}
        if gdata:
            fig = go.Figure(go.Pie(
                labels=list(gdata.keys()),
                values=list(gdata.values()),
                hole=0.65,
                marker=dict(colors=[colors[k] for k in groups if groups[k]], line=dict(color="#ffffff", width=2)),
                textinfo="label+percent",
                textfont=dict(size=11, color="#1e293b"),
                hovertemplate="<b>%{label}</b><br>R$%{value:,.2f}<extra></extra>",
            ))
            fig.add_annotation(
                text=f"<b>R${total:,.0f}</b><br><span style='font-size:11px'>Patrimônio</span>",
                x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
                font=dict(size=16, color="#0f172a"), align="center",
            )
            fig.update_layout(**{**PLOTLY_LAYOUT, "height": 300, "showlegend": False,
                                 "margin": dict(l=0, r=0, t=10, b=0)})
            st.plotly_chart(fig, width="stretch")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Manual assets ────────────────────────────────────────────────────
    section_title("Ativos Manuais")
    if "manual_assets" not in st.session_state:
        st.session_state.manual_assets = []

    with st.expander("Adicionar Ativo Manual", icon=":material/add:"):
        with st.form("add_asset"):
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("Nome", placeholder="Ex: Apartamento")
            with c2:
                value = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=1000.0)
            with c3:
                atype = st.selectbox("Tipo", ["Imóvel", "Veículo", "Cripto", "Ações", "Outro"])
            if st.form_submit_button("Adicionar", type="primary"):
                st.session_state.manual_assets.append({"name": name, "value": value, "type": atype})
                st.rerun()

    for i, asset in enumerate(st.session_state.manual_assets):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div class="row-card fade-in">
                <span style="color:var(--text-secondary);">{asset['type']} · {asset['name']}</span>
                <span style="color:var(--text-primary);font-weight:600;">R${asset['value']:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("🗑️", key=f"del_asset_{i}"):
                st.session_state.manual_assets.pop(i)
                st.rerun()

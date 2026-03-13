"""Goal configuration and progress view page."""
from __future__ import annotations

from datetime import date

import streamlit as st

from app.components.styles import page_header, section_title


def render_goals_page() -> None:
    page_header("Metas Financeiras", "Configure suas metas de vida e acompanhe o progresso")

    if "goals" not in st.session_state:
        st.session_state.goals = []

    # ── Add new goal form ────────────────────────────────────────────────
    with st.expander("Adicionar Nova Meta", expanded=len(st.session_state.goals) == 0, icon=":material/add:"):
        with st.form("new_goal_form"):
            col1, col2 = st.columns(2)
            with col1:
                goal_name = st.text_input("Nome da Meta", placeholder="Ex: Viagem ao Japão")
                target_amount = st.number_input(
                    "Valor Alvo (R$)", min_value=100.0, max_value=10_000_000.0,
                    value=10_000.0, step=500.0,
                )
            with col2:
                target_date = st.date_input(
                    "Data Alvo",
                    min_value=date.today(),
                    value=date(date.today().year + 1, 12, 31),
                )
                priority = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])

            current_saved = st.number_input(
                "Já poupado (R$)", min_value=0.0, max_value=10_000_000.0, value=0.0, step=100.0,
            )

            submitted = st.form_submit_button("Adicionar Meta", type="primary")
            if submitted and goal_name:
                months_remaining = max(
                    1,
                    (target_date.year - date.today().year) * 12
                    + (target_date.month - date.today().month),
                )
                new_goal = {
                    "name": goal_name,
                    "target_amount": target_amount,
                    "target_date": target_date.isoformat(),
                    "current_saved": current_saved,
                    "priority": priority,
                    "months_remaining": months_remaining,
                }
                st.session_state.goals.append(new_goal)
                st.success(f"Meta '{goal_name}' adicionada!")
                st.rerun()

    # ── Display existing goals ───────────────────────────────────────────
    if not st.session_state.goals:
        st.info("Nenhuma meta configurada ainda. Adicione sua primeira meta acima!")
        return

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    section_title(f"Suas Metas ({len(st.session_state.goals)})")

    priority_colors = {"Alta": "#ef4444", "Média": "#f59e0b", "Baixa": "#10b981"}

    goals_to_remove = []
    for i, goal in enumerate(st.session_state.goals):
        progress = min(1.0, goal["current_saved"] / goal["target_amount"])
        monthly_needed = (goal["target_amount"] - goal["current_saved"]) / max(1, goal["months_remaining"])
        prio_color = priority_colors.get(goal["priority"], "#64748b")

        st.markdown(f"""
        <div class="card-elevated fade-in" style="margin-bottom:0.75rem;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem;">
                <div>
                    <div style="font-size:1rem;font-weight:700;color:var(--text-primary);">{goal['name']}</div>
                    <div style="font-size:0.78rem;color:var(--text-muted);margin-top:2px;">
                        📅 Prazo: {goal['target_date']} · Mensal: R${monthly_needed:,.2f}
                    </div>
                </div>
                <span class="badge" style="background:rgba({int(prio_color[1:3],16)},{int(prio_color[3:5],16)},{int(prio_color[5:7],16)},0.1);
                       color:{prio_color};">{goal['priority']}</span>
            </div>
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.3rem;">
                <div style="flex:1;background:var(--border);border-radius:999px;height:8px;">
                    <div style="width:{progress*100:.1f}%;background:var(--accent);border-radius:999px;height:8px;
                                transition:width 0.5s ease;"></div>
                </div>
                <span style="font-size:0.82rem;font-weight:700;color:var(--accent);white-space:nowrap;">
                    {progress*100:.0f}%
                </span>
            </div>
            <div style="font-size:0.78rem;color:var(--text-muted);">
                R${goal['current_saved']:,.2f} de R${goal['target_amount']:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Remover meta", key=f"remove_goal_{i}", type="secondary"):
            goals_to_remove.append(i)

    for idx in sorted(goals_to_remove, reverse=True):
        removed = st.session_state.goals.pop(idx)
        st.success(f"Meta '{removed['name']}' removida.")
        st.rerun()

    # ── Fetch real balance from MCP ──────────────────────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("Atualizar Saldo (Open Finance)", icon=":material/refresh:"):
        with st.spinner("Conectando ao Open Finance..."):
            try:
                from src.config import settings
                from src.mcp.client import MCPClient
                client = MCPClient(mock=settings.MCP_MOCK)
                balances = client.get_balances()
                total_balance = sum(b.get("balance", 0) for b in balances)
                st.success(f"Saldo total atual: R${total_balance:,.2f}")
                st.session_state.total_balance = total_balance
            except Exception as exc:
                st.error(f"Erro ao conectar Open Finance: {exc}")

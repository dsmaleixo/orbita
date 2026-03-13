"""Automation trigger and results display page."""
from __future__ import annotations

import streamlit as st

from app.components.disclaimer import render_disclaimer
from app.components.styles import page_header, section_title


def render_reports_page() -> None:
    page_header("Relatórios & Automações", "Acione automações de análise financeira com seus dados")

    render_disclaimer()

    graph = st.session_state.get("graph")
    if graph is None:
        st.error("Sistema não inicializado. Recarregue a página.")
        return

    # ── Expense Categorization ─────────────────────────────────────────────
    section_title("Categorizar Despesas")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data inicial", key="cat_start")
    with col2:
        end_date = st.date_input("Data final", key="cat_end")

    if st.button("Categorizar Despesas", type="primary", key="btn_categorize", icon=":material/label:"):
        with st.spinner("Analisando transações..."):
            try:
                from src.graph.state import make_initial_state
                state = make_initial_state(
                    user_query="Categorize minhas despesas",
                    intent="automation",
                    automation_type="categorize",
                    automation_input={
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                    },
                )
                result = graph.invoke(state)
                st.session_state.last_categorize = result.get("automation_output", {})
                final = result.get("final_response", "")
                if final:
                    st.markdown(final)
            except Exception as exc:
                st.error(f"Erro na categorização: {exc}")

    if st.session_state.get("last_categorize"):
        categories = st.session_state.last_categorize.get("categories", {})
        if categories:
            import pandas as pd
            df = pd.DataFrame([
                {"Categoria": k.capitalize(), "Total (R$)": v["total"], "Transações": v["count"]}
                for k, v in categories.items()
            ])
            st.dataframe(df, width="stretch")
            st.bar_chart(df.set_index("Categoria")["Total (R$)"])

    st.divider()

    # ── Goal Deviation Alert ───────────────────────────────────────────────
    section_title("Verificar Desvio de Metas")
    goals = st.session_state.get("goals", [])
    if not goals:
        st.info("Configure metas na aba 'Metas' primeiro.")
    else:
        st.markdown(f"**{len(goals)}** metas ativas")
        if st.button("Verificar Metas", type="primary", key="btn_goal_alert", icon=":material/flag:"):
            with st.spinner("Verificando metas..."):
                try:
                    from src.graph.state import make_initial_state
                    state = make_initial_state(
                        user_query="Verificar desvio de metas",
                        intent="automation",
                        automation_type="goal_alert",
                        automation_input={"goals": goals},
                    )
                    result = graph.invoke(state)
                    final = result.get("final_response", "")
                    if final:
                        st.markdown(final)
                    output = result.get("automation_output", {})
                    alerts = output.get("alerts", [])
                    if alerts:
                        for alert in alerts:
                            st.warning(alert.get("message", ""))
                    else:
                        st.success("Você está no caminho certo com todas as metas!")
                except Exception as exc:
                    st.error(f"Erro na verificação de metas: {exc}")

    st.divider()

    # ── Monthly Report ─────────────────────────────────────────────────────
    section_title("Gerar Relatório Mensal")
    if st.button("Gerar Relatório", type="primary", key="btn_report", icon=":material/assessment:"):
        with st.spinner("Gerando relatório..."):
            try:
                from src.graph.state import make_initial_state
                state = make_initial_state(
                    user_query="Gerar relatório mensal",
                    intent="automation",
                    automation_type="report",
                )
                result = graph.invoke(state)
                final = result.get("final_response", "")
                if final:
                    st.markdown(final)
                st.session_state.last_report = result.get("automation_output", {})
            except Exception as exc:
                st.error(f"Erro ao gerar relatório: {exc}")

    # ── Audit log preview ──────────────────────────────────────────────────
    with st.expander("Ver Log de Auditoria MCP (últimas 10 entradas)", icon=":material/search:"):
        try:
            from src.config import settings
            log_path = settings.audit_log_path
            if log_path.exists():
                import json
                lines = log_path.read_text(encoding="utf-8").strip().split("\n")
                last_lines = lines[-10:] if len(lines) >= 10 else lines
                for line in last_lines:
                    try:
                        entry = json.loads(line)
                        blocked_label = "BLOQUEADO" if entry.get("blocked") else "OK"
                        st.code(
                            f"{blocked_label} [{entry['timestamp']}] {entry['tool']} → {entry['response_summary']}",
                            language=None,
                        )
                    except Exception:
                        st.code(line, language=None)
            else:
                st.info("Nenhuma entrada de auditoria encontrada.")
        except Exception as exc:
            st.error(f"Erro ao ler log: {exc}")

"""AI assistant chat page — routes between general LLM, RAG, and data queries."""
from __future__ import annotations

import streamlit as st

from app.components.citation import render_citations
from app.components.styles import page_header

_SUGGESTIONS = [
    ("📚", "rag",     "O que o Pai Rico ensina sobre ativos e passivos?"),
    ("📚", "rag",     "Como funciona o juros compostos?"),
    ("📊", "data",    "Quanto gastei este mês?"),
    ("📊", "data",    "Quais são minhas maiores despesas?"),
    ("💬", "general", "Como posso usar o Órbita?"),
    ("💬", "general", "O que é o Open Finance Brasil?"),
]

_ROUTE_BADGE = {
    "rag":     ("📚", "badge-info",    "Base de Conhecimento"),
    "data":    ("📊", "badge-warning", "Seus Dados"),
    "general": ("💬", "badge-neutral", "Resposta Direta"),
    "refuse":  ("🚫", "badge-danger",  "Fora do Escopo"),
}


def render_chat_page() -> None:
    page_header("Assistente Financeiro", "Pergunte sobre seus dados, conceitos financeiros ou livros clássicos")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    graph = st.session_state.get("graph")

    # Suggestion chips (shown when chat is empty)
    if not st.session_state.messages:
        cols = st.columns(3)
        for i, (icon, route, text) in enumerate(_SUGGESTIONS):
            with cols[i % 3]:
                if st.button(f"{icon} {text}", key=f"sug_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": text})
                    st.rerun()

        st.markdown("""
        <div class="card-elevated fade-in" style="margin:1rem 0 1.5rem;">
            <div style="font-size:0.92rem;font-weight:700;color:var(--text-primary);margin-bottom:0.75rem;">
                Como funciona o assistente
            </div>
            <div style="display:flex;flex-direction:column;gap:0.6rem;">
                <div style="font-size:0.82rem;color:var(--text-secondary);">
                    <span class="badge badge-info" style="margin-right:0.4rem;">📚 Conhecimento</span>
                    Conceitos financeiros e livros clássicos
                </div>
                <div style="font-size:0.82rem;color:var(--text-secondary);">
                    <span class="badge badge-warning" style="margin-right:0.4rem;">📊 Seus Dados</span>
                    Gastos, saldo e transações via Open Finance
                </div>
                <div style="font-size:0.82rem;color:var(--text-secondary);">
                    <span class="badge badge-neutral" style="margin-right:0.4rem;">💬 Direto</span>
                    Perguntas gerais respondidas sem RAG
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                intent = msg.get("intent", "general")
                icon, badge_cls, badge_label = _ROUTE_BADGE.get(intent, ("💬", "badge-neutral", ""))
                if badge_label:
                    st.markdown(
                        f'<span class="badge {badge_cls}" style="margin-bottom:0.5rem;display:inline-block;">'
                        f"{icon} {badge_label}</span>",
                        unsafe_allow_html=True,
                    )
            st.markdown(msg["content"])
            if msg.get("citations"):
                render_citations(msg["citations"])

    # Chat input
    if prompt := st.chat_input("Pergunte sobre suas finanças ou conceitos financeiros..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if graph is None:
            st.error("Assistente não inicializado. Recarregue a página.")
            return

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    from src.graph.state import make_initial_state
                    result = graph.invoke(make_initial_state(user_query=prompt))
                    intent = result.get("intent", "general")
                    response = result.get("final_response", "Não consegui gerar uma resposta.")
                    citations = result.get("citations", [])
                    body = response.split("\n\n---\n")[0].strip() if "\n\n---\n" in response else response

                    icon, badge_cls, badge_label = _ROUTE_BADGE.get(intent, ("💬", "badge-neutral", ""))
                    if badge_label:
                        st.markdown(
                            f'<span class="badge {badge_cls}" style="margin-bottom:0.5rem;display:inline-block;">'
                            f"{icon} {badge_label}</span>",
                            unsafe_allow_html=True,
                        )
                    st.markdown(body)
                    if citations:
                        render_citations(citations)

                except Exception as exc:
                    body = f"Erro ao processar: {exc}"
                    intent = "general"
                    citations = []
                    st.error(body)

        st.session_state.messages.append({
            "role": "assistant", "content": body,
            "intent": intent, "citations": citations,
        })

    if st.session_state.messages:
        if st.button("Limpar conversa", key="clear_chat", type="secondary", icon=":material/delete:"):
            st.session_state.messages = []
            st.rerun()

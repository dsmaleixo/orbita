"""Citation card renderer for Streamlit."""
from __future__ import annotations

from typing import List

import streamlit as st


def render_citations(citations: List[dict]) -> None:
    """Render citation cards as expandable sections."""
    if not citations:
        return

    st.markdown(
        '<div style="font-size:0.82rem;font-weight:600;color:var(--text-secondary);margin-top:0.75rem;">'
        '📚 Fontes</div>',
        unsafe_allow_html=True,
    )
    for i, cite in enumerate(citations, 1):
        source = cite.get("source", "Fonte desconhecida")
        page = cite.get("page", 1)
        url = cite.get("url", "")
        passage = cite.get("passage", "")

        label = f"[{i}] {source}, p.{page}"
        with st.expander(label, expanded=False, icon=":material/menu_book:"):
            if passage:
                st.markdown(f"*Trecho:* {passage}")
            if url:
                st.markdown(f"[Acessar fonte]({url})")

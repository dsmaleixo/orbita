"""Disclaimer banner component for Streamlit."""
from __future__ import annotations

from typing import List

import streamlit as st


_DEFAULT_DISCLAIMER = (
    "**Órbita é uma ferramenta educacional.** "
    "Não constitui aconselhamento financeiro. "
    "Para decisões de investimento, consulte um profissional certificado pela CVM/ANBIMA."
)


def render_disclaimer(disclaimers: List[str] | None = None) -> None:
    """Render the mandatory financial disclaimer banner."""
    if disclaimers:
        for d in disclaimers:
            text = d.replace("⚠️ ", "").strip()
            st.info(f"⚠️ {text}")
    else:
        st.info(f"⚠️ {_DEFAULT_DISCLAIMER}")

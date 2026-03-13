"""Safety/Policy agent — disclaimer injection and topic blocklist."""
from __future__ import annotations

import logging
import re
from typing import Any

from src.graph.state import OrbitaState

logger = logging.getLogger(__name__)

_MANDATORY_DISCLAIMER = (
    "⚠️ Órbita é uma ferramenta educacional. "
    "Não constitui aconselhamento financeiro. "
    "Para decisões de investimento, consulte um profissional certificado pela CVM/ANBIMA."
)

_BLOCKED_PATTERNS = [
    r"qual (ação|fundo|ativo) (devo|eu devo|posso) comprar",
    r"me recomende (um|uma) (ação|fundo|ativo)",
    r"qual o melhor (fundo|ação|papel) para (eu )?investir",
    r"como (eu )?pag[ao] menos imposto",
    r"estratégia tributária",
    r"devo colocar (\d+)% em",
    r"quanto (colocar|investir|aportar) em cada",
    r"monte minha carteira",
    r"me dê conselh[oa] de investimento",
]

_ADVISORY_TOPICS = [
    "ação específica",
    "ticker específico",
    "portfólio alocação",
    "percentual de carteira",
]


def safety_node(state: OrbitaState) -> dict[str, Any]:
    """Check for blocked topics and inject mandatory disclaimers."""
    query = state["user_query"].lower()
    disclaimers = list(state.get("disclaimers", []))

    # Add mandatory disclaimer to all responses
    if _MANDATORY_DISCLAIMER not in disclaimers:
        disclaimers.append(_MANDATORY_DISCLAIMER)

    # Check for blocked patterns
    for pattern in _BLOCKED_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            logger.info("Safety: blocked query matching pattern: %s", pattern)
            return {
                "is_blocked": True,
                "block_reason": "Essa pergunta pede aconselhamento financeiro personalizado, "
                                "o que está fora do escopo educacional do Órbita. "
                                "Consulte um profissional certificado.",
                "disclaimers": disclaimers,
                "final_response": (
                    "Não posso responder a essa pergunta, pois constitui aconselhamento "
                    "financeiro personalizado. O Órbita é uma ferramenta educacional e "
                    "não fornece recomendações de investimento específicas.\n\n"
                    + _MANDATORY_DISCLAIMER
                ),
            }

    # If intent is refuse (set by supervisor), also block
    if state.get("intent") == "refuse":
        logger.info("Safety: blocking due to supervisor refuse intent")
        return {
            "is_blocked": True,
            "block_reason": "Fora do escopo educacional do Órbita.",
            "disclaimers": disclaimers,
            "final_response": (
                "Esta pergunta está fora do escopo do Órbita. "
                "Posso ajudar com educação financeira, conceitos sobre produtos financeiros, "
                "FGTS, seguro-desemprego, planejamento financeiro básico, e similares.\n\n"
                + _MANDATORY_DISCLAIMER
            ),
        }

    logger.info("Safety: query approved, disclaimers injected")
    return {
        "is_blocked": False,
        "block_reason": None,
        "disclaimers": disclaimers,
    }

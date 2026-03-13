"""Automation agent — expense categorization, goal alerts, and report generation."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from src.config import settings
from src.graph.state import OrbitaState

logger = logging.getLogger(__name__)

_MANDATORY_DISCLAIMER = (
    "⚠️ Órbita é uma ferramenta educacional. Não constitui aconselhamento financeiro."
)

_CATEGORY_MAP = {
    "alimentacao": ["supermercado", "restaurante", "ifood", "lanche", "padaria", "mercado", "uber eats"],
    "transporte": ["uber", "99taxi", "combustivel", "estacionamento", "metro", "onibus", "transporte"],
    "moradia": ["aluguel", "condominio", "luz", "agua", "gas", "internet", "telefone"],
    "saude": ["farmacia", "medico", "hospital", "plano de saude", "academia", "drogaria"],
    "educacao": ["escola", "faculdade", "curso", "livro", "material escolar", "spotify", "netflix"],
    "lazer": ["cinema", "teatro", "viagem", "hotel", "bar", "balada", "show", "jogo"],
    "vestuario": ["roupa", "calcado", "acessorio", "loja de roupas"],
    "investimentos": ["tesouro", "cdb", "fundo", "corretora", "investimento", "aplicacao"],
    "outros": [],
}


def _categorize_transaction(description: str) -> str:
    """Map a transaction description to a spending category."""
    desc_lower = description.lower()
    for category, keywords in _CATEGORY_MAP.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "outros"


def _run_categorize(transactions: List[Dict]) -> Dict:
    """Categorize a list of transactions."""
    result = {}
    for txn in transactions:
        category = _categorize_transaction(txn.get("description", ""))
        if category not in result:
            result[category] = {"count": 0, "total": 0.0, "transactions": []}
        result[category]["count"] += 1
        result[category]["total"] += abs(txn.get("amount", 0))
        result[category]["transactions"].append({
            "description": txn.get("description", ""),
            "amount": txn.get("amount", 0),
            "date": txn.get("date", ""),
        })

    # Sort by total descending
    sorted_result = dict(sorted(result.items(), key=lambda x: x[1]["total"], reverse=True))
    return {"categories": sorted_result, "total_transactions": len(transactions)}


def _run_goal_alert(transactions: List[Dict], goals: List[Dict]) -> Dict:
    """Compare spending trajectory against declared goals."""
    total_spending = sum(abs(t.get("amount", 0)) for t in transactions if t.get("amount", 0) < 0)
    total_income = sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) > 0)
    savings = total_income - total_spending
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0

    alerts = []
    for goal in goals:
        target = goal.get("target_amount", 0)
        months_remaining = goal.get("months_remaining", 12)
        monthly_required = target / months_remaining if months_remaining > 0 else target
        if savings < monthly_required:
            shortfall = monthly_required - savings
            alerts.append({
                "goal": goal.get("name", "Meta"),
                "required_monthly": round(monthly_required, 2),
                "current_savings": round(savings, 2),
                "shortfall": round(shortfall, 2),
                "message": (
                    f"Para atingir sua meta '{goal.get('name', '')}' de R${target:,.2f}, "
                    f"você precisa poupar R${monthly_required:,.2f}/mês. "
                    f"Este mês você poupou R${savings:,.2f} (faltam R${shortfall:,.2f})."
                ),
            })

    return {
        "total_income": round(total_income, 2),
        "total_spending": round(total_spending, 2),
        "savings": round(savings, 2),
        "savings_rate_pct": round(savings_rate, 1),
        "alerts": alerts,
        "num_alerts": len(alerts),
    }


def _run_report(transactions: List[Dict], balances: List[Dict]) -> Dict:
    """Generate a structured monthly financial summary."""
    total_income = sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) > 0)
    total_expenses = sum(abs(t.get("amount", 0)) for t in transactions if t.get("amount", 0) < 0)
    net = total_income - total_expenses

    categorized = _run_categorize(transactions)
    top_categories = list(categorized["categories"].items())[:3]

    total_balance = sum(b.get("balance", 0) for b in balances)

    report = {
        "period": datetime.now().strftime("%B %Y"),
        "summary": {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_result": round(net, 2),
            "total_balance": round(total_balance, 2),
        },
        "top_spending_categories": [
            {"category": cat, "total": round(data["total"], 2), "count": data["count"]}
            for cat, data in top_categories
        ],
        "insights": [],
    }

    # Generate insights
    if net < 0:
        report["insights"].append(f"⚠️ Deficit de R${abs(net):,.2f} neste período. Revise seus gastos.")
    else:
        report["insights"].append(f"✅ Você poupou R${net:,.2f} este mês. Continue assim!")

    if top_categories:
        top_cat, top_data = top_categories[0]
        pct = (top_data["total"] / total_expenses * 100) if total_expenses > 0 else 0
        report["insights"].append(
            f"💰 Maior categoria de gasto: {top_cat} (R${top_data['total']:,.2f}, {pct:.0f}% das despesas)."
        )

    return report


def _format_automation_result(automation_type: str, output: Dict) -> str:
    """Format automation output as human-readable text."""
    if automation_type == "categorize":
        lines = ["📊 **Categorização de Despesas**\n"]
        for cat, data in output.get("categories", {}).items():
            lines.append(f"- **{cat.capitalize()}**: R${data['total']:,.2f} ({data['count']} transações)")
        lines.append(f"\n_Total: {output.get('total_transactions', 0)} transações analisadas_")
        return "\n".join(lines)

    elif automation_type == "goal_alert":
        lines = [
            f"🎯 **Análise de Metas**\n",
            f"Receita: R${output.get('total_income', 0):,.2f}",
            f"Despesas: R${output.get('total_spending', 0):,.2f}",
            f"Poupança: R${output.get('savings', 0):,.2f} ({output.get('savings_rate_pct', 0):.1f}%)",
        ]
        for alert in output.get("alerts", []):
            lines.append(f"\n⚠️ {alert['message']}")
        if not output.get("alerts"):
            lines.append("\n✅ Você está no caminho certo com suas metas!")
        return "\n".join(lines)

    elif automation_type == "report":
        summary = output.get("summary", {})
        lines = [
            f"📈 **Relatório Financeiro — {output.get('period', '')}**\n",
            f"Receitas: R${summary.get('total_income', 0):,.2f}",
            f"Despesas: R${summary.get('total_expenses', 0):,.2f}",
            f"Resultado: R${summary.get('net_result', 0):,.2f}",
            f"Saldo Total: R${summary.get('total_balance', 0):,.2f}",
            "\n**Principais gastos:**",
        ]
        for cat_info in output.get("top_spending_categories", []):
            lines.append(f"- {cat_info['category'].capitalize()}: R${cat_info['total']:,.2f}")
        lines.append("\n**Insights:**")
        for insight in output.get("insights", []):
            lines.append(f"- {insight}")
        return "\n".join(lines)

    return str(output)


def automation_node(state: OrbitaState) -> dict[str, Any]:
    """Execute automation workflow based on automation_type in state."""
    automation_type = state.get("automation_type", "categorize")
    automation_input = state.get("automation_input") or {}

    logger.info("Automation: running workflow '%s'", automation_type)

    # Import MCP client (uses mock if MCP_MOCK=true)
    from src.mcp.client import MCPClient
    client = MCPClient(mock=settings.MCP_MOCK)

    mcp_tool_calls = list(state.get("mcp_tool_calls", []))

    try:
        # Fetch data via MCP
        if automation_type in ("categorize", "goal_alert", "report"):
            start_date = automation_input.get("start_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
            end_date = automation_input.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            transactions = client.get_transactions(start_date, end_date)
            mcp_tool_calls.append({
                "tool": "get_transactions",
                "params": {"start_date": start_date, "end_date": end_date},
                "record_count": len(transactions),
            })

        balances = []
        if automation_type == "report":
            balances = client.get_balances()
            mcp_tool_calls.append({"tool": "get_balances", "params": {}, "record_count": len(balances)})

        # Run the selected workflow
        if automation_type == "categorize":
            output = _run_categorize(transactions)
        elif automation_type == "goal_alert":
            goals = automation_input.get("goals", [{"name": "Reserva de Emergência", "target_amount": 30000, "months_remaining": 6}])
            output = _run_goal_alert(transactions, goals)
        elif automation_type == "report":
            output = _run_report(transactions, balances)
        else:
            output = {"error": f"Unknown automation type: {automation_type}"}

        formatted = _format_automation_result(automation_type, output)
        final_response = formatted + "\n\n---\n" + _MANDATORY_DISCLAIMER

        logger.info("Automation: workflow '%s' completed successfully", automation_type)

    except Exception as exc:
        logger.error("Automation error: %s", exc)
        output = {"error": str(exc)}
        final_response = f"Erro na automação: {exc}\n\n{_MANDATORY_DISCLAIMER}"

    return {
        "automation_output": output,
        "mcp_tool_calls": mcp_tool_calls,
        "final_response": final_response,
    }

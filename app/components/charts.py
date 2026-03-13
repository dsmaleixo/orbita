"""Reusable Plotly chart components with the Órbita light theme."""
from __future__ import annotations

from typing import Dict, List

import plotly.graph_objects as go
import streamlit as st

from app.components.styles import CATEGORY_COLORS, CHART_COLORS, PLOTLY_LAYOUT


def _apply_layout(fig: go.Figure, **overrides) -> go.Figure:
    layout = {**PLOTLY_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig


def _title(text: str) -> dict:
    return dict(text=f"<b>{text}</b>", font=dict(size=14, color="#0f172a", family="Inter"))


def bar_chart_income_expense(monthly_data: List[Dict]) -> None:
    """Grouped bar chart: income vs expenses by month."""
    if not monthly_data:
        st.info("Sem dados para exibir.")
        return

    months = [d["month"] for d in monthly_data]
    income = [d["income"] for d in monthly_data]
    expenses = [d["expenses"] for d in monthly_data]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Receitas",
        x=months, y=income,
        marker_color="#10b981",
        marker_line_width=0,
        text=[f"R${v:,.0f}" for v in income],
        textposition="outside",
        textfont=dict(size=10, color="#10b981"),
    ))
    fig.add_trace(go.Bar(
        name="Despesas",
        x=months, y=expenses,
        marker_color="#ef4444",
        marker_line_width=0,
        text=[f"R${v:,.0f}" for v in expenses],
        textposition="outside",
        textfont=dict(size=10, color="#ef4444"),
    ))
    fig = _apply_layout(fig,
        barmode="group",
        bargap=0.25, bargroupgap=0.08,
        title=_title("Fluxo de Caixa Mensal"),
        showlegend=True,
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], tickprefix="R$", tickformat=",.0f"),
        height=320,
    )
    st.plotly_chart(fig, width="stretch")


def donut_chart_categories(category_data: Dict[str, float]) -> None:
    """Donut chart for spending by category."""
    if not category_data:
        st.info("Sem dados de categorias.")
        return

    labels = [k.capitalize() for k in category_data.keys()]
    values = list(category_data.values())
    colors = [CATEGORY_COLORS.get(k, "#64748b") for k in category_data.keys()]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.65,
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#1e293b"),
        hovertemplate="<b>%{label}</b><br>R$%{value:,.2f}<br>%{percent}<extra></extra>",
    ))
    total = sum(values)
    fig.add_annotation(
        text=f"<b>R${total:,.0f}</b><br><span style='font-size:11px;color:#94a3b8'>Total</span>",
        x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False, font=dict(size=16, color="#0f172a"),
        align="center",
    )
    fig = _apply_layout(fig,
        title=_title("Gastos por Categoria"),
        showlegend=True,
        legend=dict(**PLOTLY_LAYOUT["legend"], orientation="v", x=1.05),
        height=320,
    )
    st.plotly_chart(fig, width="stretch")


def line_chart_balance(balance_history: List[Dict]) -> None:
    """Line chart showing balance evolution over time."""
    if not balance_history:
        st.info("Sem histórico de saldo.")
        return

    dates = [d["date"] for d in balance_history]
    balances = [d["balance"] for d in balance_history]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=balances,
        mode="lines",
        line=dict(color="#6366f1", width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.06)",
        hovertemplate="<b>%{x}</b><br>R$%{y:,.2f}<extra></extra>",
        name="Saldo",
    ))
    fig = _apply_layout(fig,
        title=_title("Evolução do Saldo"),
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], tickprefix="R$", tickformat=",.0f"),
        height=260,
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def horizontal_bar_categories(category_data: Dict[str, float], top_n: int = 8) -> None:
    """Horizontal bar chart for category spending."""
    if not category_data:
        return

    sorted_cats = sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:top_n]
    cats = [k.capitalize() for k, _ in sorted_cats]
    vals = [v for _, v in sorted_cats]
    colors = [CATEGORY_COLORS.get(k.lower(), "#64748b") for k, _ in sorted_cats]

    fig = go.Figure(go.Bar(
        x=vals, y=cats,
        orientation="h",
        marker_color=colors,
        marker_line_width=0,
        text=[f"R${v:,.0f}" for v in vals],
        textposition="outside",
        textfont=dict(size=11, color="#64748b"),
        hovertemplate="<b>%{y}</b><br>R$%{x:,.2f}<extra></extra>",
    ))
    fig = _apply_layout(fig,
        title=_title("Maiores Categorias de Gasto"),
        xaxis=dict(**PLOTLY_LAYOUT["xaxis"], tickprefix="R$", tickformat=",.0f"),
        height=max(250, len(cats) * 38),
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def area_chart_cashflow(cashflow_data: List[Dict]) -> None:
    """Area chart for cumulative cash flow."""
    if not cashflow_data:
        return

    dates = [d["date"] for d in cashflow_data]
    cumulative = [d["cumulative"] for d in cashflow_data]

    fig = go.Figure()
    color = "#10b981" if (cumulative[-1] if cumulative else 0) >= 0 else "#ef4444"
    fig.add_trace(go.Scatter(
        x=dates, y=cumulative,
        mode="lines",
        line=dict(color=color, width=2, shape="spline"),
        fill="tozeroy",
        fillcolor=f"rgba({int(color[1:3], 16)},{int(color[3:5], 16)},{int(color[5:7], 16)},0.06)",
        hovertemplate="<b>%{x}</b><br>R$%{y:,.2f}<extra></extra>",
        name="Saldo Acumulado",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="#cbd5e1", line_width=1)
    fig = _apply_layout(fig,
        title=_title("Fluxo Acumulado no Período"),
        yaxis=dict(**PLOTLY_LAYOUT["yaxis"], tickprefix="R$", tickformat=",.0f"),
        height=260,
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def sparkline(values: List[float], color: str = "#6366f1") -> str:
    """Return an inline SVG sparkline (used in cards)."""
    if len(values) < 2:
        return ""
    w, h = 80, 28
    mn, mx = min(values), max(values)
    rng = mx - mn or 1
    pts = []
    for i, v in enumerate(values):
        x = i / (len(values) - 1) * w
        y = h - (v - mn) / rng * h
        pts.append(f"{x:.1f},{y:.1f}")
    points = " ".join(pts)
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<polyline points="{points}" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>'
    )

"""Mock MCP server with synthetic Brazilian transaction data.

Used for demo/testing when real Pluggy credentials are not available.
All data is synthetic — no real financial information.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, List


_SYNTHETIC_MERCHANTS = {
    "alimentacao": ["Supermercado Extra", "iFood", "McDonald's Brasil", "Padaria Central", "Restaurante do Bairro"],
    "transporte": ["Uber Brasil", "99Taxi", "Posto Shell", "Estacionamento Shopping", "Metrô SP"],
    "moradia": ["Aluguel Ap", "Condomínio Residencial", "Enel Energia", "Sabesp", "Claro Internet"],
    "saude": ["Drogasil", "UPA Saúde", "Academia SmartFit", "Plano de Saúde"],
    "lazer": ["Cinema Cinemark", "Netflix", "Spotify", "Bar do João", "Livraria Cultura"],
    "educacao": ["Faculdade Online", "Udemy", "Inglês Prime", "Material Escolar"],
    "vestuario": ["Renner", "Riachuelo", "Nike Store", "Netshoes"],
}

_SYNTHETIC_AMOUNTS = {
    "alimentacao": (-800, -50),
    "transporte": (-200, -10),
    "moradia": (-2500, -150),
    "saude": (-500, -30),
    "lazer": (-400, -20),
    "educacao": (-600, -50),
    "vestuario": (-600, -80),
}


def _generate_transactions(start_date: str, end_date: str) -> List[Dict]:
    """Generate synthetic transaction data for the given date range."""
    random.seed(42)  # Deterministic for testing

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days + 1

    transactions = []
    txn_id = 1000

    # Monthly salary on the 5th
    for month_offset in range(max(1, days // 30)):
        salary_date = start + timedelta(days=5 + month_offset * 30)
        if salary_date <= end:
            transactions.append({
                "id": f"TXN{txn_id:04d}",
                "date": salary_date.strftime("%Y-%m-%d"),
                "description": "Salário Empresa ABC",
                "amount": 4500.00,
                "category": "receita",
                "account_id": "ACC001",
            })
            txn_id += 1

    # Random expenses throughout the period
    for _ in range(min(50, days * 2)):
        category = random.choice(list(_SYNTHETIC_MERCHANTS.keys()))
        merchant = random.choice(_SYNTHETIC_MERCHANTS[category])
        min_amt, max_amt = _SYNTHETIC_AMOUNTS[category]
        amount = round(random.uniform(min_amt, max_amt), 2)
        txn_date = start + timedelta(days=random.randint(0, days - 1))

        transactions.append({
            "id": f"TXN{txn_id:04d}",
            "date": txn_date.strftime("%Y-%m-%d"),
            "description": merchant,
            "amount": amount,
            "category": category,
            "account_id": "ACC001",
        })
        txn_id += 1

    # Sort by date
    transactions.sort(key=lambda x: x["date"])
    return transactions


def _generate_balances() -> List[Dict]:
    """Generate synthetic account balance data."""
    return [
        {
            "account_id": "ACC001",
            "account_type": "corrente",
            "institution": "Banco Digital XYZ",
            "balance": 2847.50,
            "currency": "BRL",
        },
        {
            "account_id": "ACC002",
            "account_type": "poupanca",
            "institution": "Banco Digital XYZ",
            "balance": 8200.00,
            "currency": "BRL",
        },
    ]


def _generate_accounts() -> List[Dict]:
    """Generate synthetic account metadata."""
    return [
        {
            "account_id": "ACC001",
            "account_type": "corrente",
            "institution": "Banco Digital XYZ",
            "agency": "0001",
            "last_four": "5678",
            "status": "active",
        },
        {
            "account_id": "ACC002",
            "account_type": "poupanca",
            "institution": "Banco Digital XYZ",
            "agency": "0001",
            "last_four": "9012",
            "status": "active",
        },
    ]


class MockMCPServer:
    """In-memory mock MCP server returning synthetic Brazilian financial data."""

    def get_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        return _generate_transactions(start_date, end_date)

    def get_balances(self) -> List[Dict]:
        return _generate_balances()

    def get_accounts(self) -> List[Dict]:
        return _generate_accounts()

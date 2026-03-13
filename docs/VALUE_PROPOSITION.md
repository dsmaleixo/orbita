# Órbita — Value Proposition

## 1. The Problem

Brazil has 70M+ adults under 35 navigating financial decisions with tools built for a different era. Traditional finance apps demand the user become their own accountant — manual entry, manual categorization, manual interpretation. The result is predictable: **over 60% of personal finance app users abandon within 90 days** (Sensor Tower, FinTech market data). Meanwhile, **47% of Generation Z young adults exercise no financial control** (SPC Brasil / CNDL).

The cost isn't abstract. Every month without financial visibility is a month where:
- R$200–500 in avoidable spending leaks go undetected
- Compound growth on savings goals is lost permanently
- Major life milestones (first apartment, wedding, career transition) drift further away

Existing solutions fail on a structural level. **GuiaBolso** pioneered Open Banking integration but plateaued with a passive dashboard model. **Mobills and Organizze** remain glorified spreadsheets. **Neobank features** (Nubank, Neon) are limited to transaction categorization without goal intelligence. None of them answer the only question that matters to a 26-year-old professional: *"Am I on track for the life I actually want?"*

---

## 2. The Solution

Órbita is an **agentic financial assistant** that replaces manual tracking with continuous, goal-aware intelligence. It is built on three pillars:

### Connect once, never manage again
Through Open Finance Brasil integration via [Pluggy](https://pluggy.ai), Órbita ingests transaction data automatically using the official Connect Widget embedded inside the app. No manual entry. No CSV imports. No photo receipts. The user connects their bank once and the system handles the rest. Real-time event webhooks (FastAPI receiver) keep data fresh as transactions arrive.

### An assistant that knows your data and the literature
Órbita routes every user query to the right source of truth:

- **Personal financial questions** ("What did I spend this month?", "Am I saving enough?") are answered by querying the user's own Open Finance data via MCP — with numbers, not generalities.
- **Financial education questions** ("What is CDI?", "How does Tesouro Direto work?") are answered by a RAG pipeline indexed over official Brazilian financial education materials (BACEN, CVM, Procon) and classic personal finance literature, with full citation transparency.
- **Conversational questions** are handled by a direct LLM path with no retrieval overhead.
- **Regulated investment advice** is explicitly refused with a clear explanation.

### Trustworthy education, not social media tips
Órbita never acts as an investment advisor. Every educational response is grounded in publicly available, regulatory-compliant materials with `[Source, p.X]` citations and a Self-RAG anti-hallucination check — if a claim can't be traced to evidence, the system refuses rather than fabricates.

---

## 3. PoC Scope and Boundaries

This project is an **academic proof of concept** that validates the core architectural thesis: that a multi-agent LangGraph system can combine personal Open Finance data with RAG-backed financial education to deliver goal-aware, citation-verified guidance — locally, at zero API cost, with strict data sovereignty.

### What the PoC demonstrates

| Capability | Implementation |
|---|---|
| **Multi-agent orchestration** | LangGraph `StateGraph` with 8 specialized agents, 4-route intent topology, conditional edges, and retry loop |
| **4-route intent routing** | `general` (direct LLM) / `rag` (retrieval pipeline) / `data` (personal MCP data) / `refuse` (blocked topics) |
| **Self-RAG anti-hallucination** | Claim-level grounding check; 1 re-retrieval attempt; explicit refusal if still unsupported |
| **Open Finance integration** | Pluggy REST API via `PluggyDirectClient`; in-app Connect Widget; real-time webhook server |
| **MCP security** | Read-only allowlist (3 tools); every call audit-logged; output sanitized before LLM context |
| **Local-first infrastructure** | Ollama (`llama3.1:8b`), FAISS, `BAAI/bge-m3` — no SaaS, no API cost, full data sovereignty |
| **Multi-page financial dashboard** | 9 Streamlit pages (Dashboard, Transactions, Cash Flow, Accounts, Assets, Recurring, Categories, Chat, Connect) |
| **Automation workflows** | Expense categorization, goal deviation alerts, financial report generation |
| **Evaluation suite** | RAGAS metrics (15-question golden set), 5 automation task definitions |

### What the PoC does not cover
- Production-grade security, scalability, or multi-user infrastructure
- Real monetization or go-to-market execution
- Full regulatory compliance (CVM/BACEN advisory limits)
- Couples or shared goal features
- Real-time streaming or background sync daemons (automation is on-demand batch)

---

## 4. Value Proposition Canvas

### Customer Profile

| **Customer Jobs** | **Pains** | **Gains** |
|---|---|---|
| Save for major life milestones (apartment, wedding, car) | Manual tracking is tedious and gets abandoned within weeks | Feel in control of their financial future without daily effort |
| Understand where money actually goes each month | No clear connection between daily spending and long-term goal progress | Confidence that life milestones are achievable on a concrete timeline |
| Build financial discipline without becoming a "finance person" | Guilt and anxiety from impulse spending with no feedback loop | Automated visibility that eliminates the "head in the sand" pattern |
| Get trustworthy answers to financial questions | Fear of bad advice; distrust of social media "get rich" content | Cited, source-backed financial education that builds real literacy |
| Maintain progress consistently over months/years | Life gets busy — financial management is the first thing dropped | A system that works even when the user isn't actively managing |

### Value Map

| **Products & Services** | **Pain Relievers** | **Gain Creators** |
|---|---|---|
| Open Finance auto-sync (Pluggy Connect Widget + webhooks) | Eliminates the #1 cause of abandonment: data-entry friction | One-time setup creates permanent, always-current financial visibility |
| 4-route intelligent assistant (general / RAG / data / refuse) | Right answer from the right source every time — no over-fetching, no hallucinations | Users trust the assistant because it knows when to refuse |
| Self-RAG citation pipeline (BACEN, CVM, Procon, books) | Removes the risk of acting on unverified financial "tips" | Every educational response carries a traceable source |
| Personal data queries via MCP | Answers questions about *the user's own finances*, not generic advice | Contextual, personalized insights without sharing data externally |
| Automation workflows (categorize, goal alerts, reports) | Breaks the "check once a month, panic, give up" cycle | Course-correction in near real-time, not retroactively |

---

## 5. Competitive Positioning

> **For young Brazilian professionals planning major life milestones** who are frustrated by finance apps that demand constant manual input and deliver passive dashboards, **Órbita** is an **agentic financial assistant** that connects to Open Finance automatically, answers questions about both financial concepts and your own data with citation-backed accuracy, and intervenes proactively when you go off course — so you build the future you want without becoming your own accountant. **Unlike GuiaBolso, Mobills, or neobank built-in tools**, Órbita doesn't just report on the past — it actively guides the path forward, and it never makes things up.

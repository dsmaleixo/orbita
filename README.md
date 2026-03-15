# Órbita — Assistente Financeiro Agentico para Jovens Brasileiros

> **Prova de conceito acadêmica** de um sistema agentico multi-agente com RAG, orquestrado por LangGraph, conectado ao Open Finance Brasil via MCP (Pluggy), para educação financeira de jovens adultos brasileiros.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Visão Geral

**Problema:** 60% dos jovens brasileiros abandonam apps de finanças pessoais. O mercado oferece dashboards passivos que exigem entrada manual de dados.

**Solução:** Órbita combina um assistente financeiro agentico com um dashboard moderno:

- **Dashboard financeiro** completo — saldos, transações, fluxo de caixa, categorias, metas e patrimônio
- **Assistente IA** com 4 rotas inteligentes — RAG para educação financeira, dados pessoais via Open Finance, conversa geral e recusa segura
- **Citações verificáveis** de fontes oficiais (BACEN, CVM, Procon)
- **Anti-alucinação** via Self-RAG com re-retrieval automático
- **Zero entrada manual** — sincronização via Open Finance Brasil (Pluggy)

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Next.js + React + Tailwind CSS)              │
│  11 páginas: Dashboard, Transações, Fluxo de Caixa,    │
│  Contas, Patrimônio, Recorrentes, Categorias, Metas,   │
│  Relatórios, Assistente IA, Conectar Banco              │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP (proxy :3000 → :8001)
┌───────────────────────▼─────────────────────────────────┐
│  API (FastAPI)                                          │
│  REST endpoints + LangGraph agent invocation            │
└───────────┬───────────────────────┬─────────────────────┘
            │                       │
┌───────────▼───────────┐ ┌────────▼──────────────────────┐
│  MCP Client (stdio)   │ │  LangGraph Orchestration      │
│  → Pluggy MCP Server  │ │  Supervisor → Retriever →     │
│  (Open Finance)       │ │  Safety → Writer → Self-Check │
└───────────────────────┘ └────────┬──────────────────────┘
                                   │
                          ┌────────▼──────────┐
                          │  FAISS + bge-m3   │
                          │  (RAG pipeline)   │
                          └───────────────────┘
```

### Agentes LangGraph

| Agente | Rota | Responsabilidade |
|---|---|---|
| **Supervisor** | Entrada | Classifica intenção: `general` / `rag` / `data` / `refuse` |
| **General** | `general` | Resposta direta via Ollama, sem retrieval |
| **Data Query** | `data` | Busca dados financeiros via MCP, responde com contexto real |
| **Retriever** | `rag` | Busca densa em FAISS (top-5) + reranking opcional |
| **Safety** | `rag` | Disclaimers obrigatórios, bloqueio de aconselhamento regulado |
| **Writer** | `rag` | Resposta com citações `[Fonte: X, p.Y]` |
| **Self-Check** | `rag` | Validação Self-RAG: re-retrieval ou recusa se não suportado |
| **Automation** | automação | Categorização, alertas de metas, relatórios financeiros |

---

## Stack Técnica

| Componente | Tecnologia |
|---|---|
| Frontend | Next.js 15, React 19, Tailwind CSS 4, Recharts, Lucide Icons |
| API | FastAPI + Uvicorn |
| Orquestração | LangGraph 0.2+ (StateGraph com estado tipado) |
| LLM | Ollama + Llama 3.1 8B (local, zero custo) |
| Embeddings | BAAI/bge-m3 (1024-dim, multilingual) |
| Vector Store | FAISS (faiss-cpu, persistência local) |
| Open Finance | Pluggy REST API via MCP (allowlist + audit logging) |
| Avaliação | RAGAS (Faithfulness, Relevancy, Precision, Recall) |
| Testes | pytest (totalmente mockado) |

---

## Setup

### Pré-requisitos

- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com/) instalado localmente
- [uv](https://docs.astral.sh/uv/) para gerenciamento de dependências Python

### 1. Clone e instale dependências

```bash
git clone https://github.com/dsmaleixo/orbita.git
cd orbita

# Backend (Python)
uv sync

# Frontend (Node.js)
cd frontend && npm install && cd ..
```

### 2. Configure o ambiente

```bash
cp .env.example .env
# Edite .env conforme necessário
```

### 3. Instale o modelo LLM

```bash
ollama pull llama3.1:8b
```

### 4. Execute o pipeline de ingestão (uma vez)

```bash
uv run python -m ingest.pipeline
```

Isso irá baixar documentos do BACEN, CVM, Procon-SP, B3, segmentar em chunks, indexar com bge-m3 e salvar no FAISS.

### 5. Execute o app

```bash
# Terminal 1 — API (porta 8001)
uv run python api/main.py

# Terminal 2 — Frontend (porta 3000)
cd frontend && npm run dev
```

Acesse em: **http://localhost:3000**

### 6. Execute os testes

```bash
uv run pytest tests/ -v
```

---

## Docker

```bash
docker-compose up --build

# Puxar o modelo no primeiro uso
docker exec orbita-ollama-1 ollama pull llama3.1:8b

# Pipeline de ingestão no container
docker exec orbita-orbita-1 python -m ingest.pipeline
```

Portas expostas: `3000` (frontend) e `8001` (API).

---

## MCP — Segurança

### Ferramentas Expostas (somente leitura)

| Tool | Descrição |
|---|---|
| `get_transactions` | Transações bancárias por período |
| `get_balances` | Saldos das contas vinculadas |
| `get_accounts` | Metadados das contas |

### O que o agente NÃO pode fazer

Criar/deletar transações, transferir fundos, criar pagamentos, autenticar, escrever dados no Open Finance.

### Controles

- **Allowlist** — `config/mcp_allowlist.yaml` restringe ferramentas permitidas
- **Audit logging** — toda chamada MCP registrada em `logs/mcp_audit.log`
- **Sanitização** — caracteres de controle removidos, campos truncados, valores financeiros nunca logados

---

## Avaliação

### RAG — RAGAS

```bash
uv run python eval/run_ragas.py
```

15 perguntas rotuladas (10 educação financeira + 3 adversariais + 2 recusas).

| Métrica | Meta |
|---|---|
| Faithfulness | >= 0.70 |
| Answer Relevancy | >= 0.70 |
| Context Precision | >= 0.65 |
| Context Recall | >= 0.65 |
| Correct Refusals | = 2/2 |

### Automação

```bash
uv run python eval/run_automation_eval.py
```

5 tarefas: categorização, detecção de desvio de meta, relatório mensal, alerta de gastos, detecção de ausência de poupança. Meta: >= 80%.

---

## Estrutura do Repositório

```
orbita/
├── api/                          # FastAPI REST API
│   └── main.py                   # Endpoints + LangGraph integration
│
├── frontend/                     # Next.js frontend
│   ├── src/app/                  # Pages (11 rotas)
│   ├── src/components/           # UI components (React)
│   └── src/lib/                  # API client + utilities
│
├── src/                          # Core Python backend
│   ├── config.py                 # Configuração centralizada (.env)
│   ├── agents/                   # 8 agentes LangGraph
│   ├── data/                     # Transformações de dados
│   ├── graph/                    # StateGraph + OrbitaState
│   ├── mcp/                      # Cliente MCP + segurança + Pluggy
│   ├── rag/                      # Embeddings + FAISS + Reranker
│   └── webhook/                  # FastAPI webhook receiver (Pluggy)
│
├── ingest/                       # Pipeline de ingestão offline
│   ├── pipeline.py               # Orchestrador end-to-end
│   ├── loaders.py                # PDF + HTML loaders
│   ├── splitter.py               # Chunking (512 tokens)
│   └── sources.yaml              # Fontes BACEN/CVM/Procon/B3
│
├── config/                       # Arquivos de configuração
│   └── mcp_allowlist.yaml        # Allowlist de ferramentas MCP
│
├── eval/                         # Suítes de avaliação
│   ├── golden_set.json           # 15 Q&As rotuladas
│   ├── automation_tasks.json     # 5 tarefas de automação
│   ├── run_ragas.py              # Avaliação RAGAS
│   └── run_automation_eval.py    # Avaliação de automação
│
├── tests/                        # Testes unitários (mockados)
├── data/                         # Dados e índice FAISS
├── logs/                         # Logs de auditoria MCP
├── docs/                         # Documentação técnica
│   ├── ARCHITECTURE.md           # Especificação arquitetural
│   ├── VALUE_PROPOSITION.md      # Proposta de valor
│   ├── IMPLEMENTATION_INSTRUCTIONS.md  # Especificação acadêmica
│   └── PLUGGY.md                 # Documentação Pluggy
│
├── Dockerfile                    # Build multi-stage (Python + Node)
├── docker-compose.yml
├── pyproject.toml                # Dependências Python (uv)
├── CITATION.cff
└── LICENSE                       # MIT
```

---

## Limitações

1. **LLM em português** — Llama 3.1 8B pode ter desempenho variável em termos financeiros específicos
2. **Latência** — 2-3 chamadas de LLM por resposta = 20-30s no P50
3. **Corpus** — fallback para corpus sintético quando documentos oficiais não estão disponíveis
4. **Pluggy** — requer credenciais de sandbox ou produção (obtenha em dashboard.pluggy.ai)

---

## Licença

MIT License — veja [LICENSE](LICENSE).

---

*Órbita é uma ferramenta educacional. Não constitui aconselhamento financeiro. Para decisões de investimento, consulte um profissional certificado pela CVM/ANBIMA.*

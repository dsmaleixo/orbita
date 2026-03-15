### Objetivo

Em grupos de até dois aluno(a)s, construir uma prova de conceito (PoC) open source de um **sistema agêntico** (LangChain) que resolva um problema em **saúde, educação, meio ambiente, inclusão digital, justiça social ou em outra direção que tenha apelo social**.

O sistema deve:

1. **Indexar** um conjunto de documentos públicos/abertos (PDFs, sites, bases abertas).
2. **Responder com citações** (passagens/URLs e metadados, como página/trecho).
3. Ter mecanismo **antialucinação (self-check)**: recusa ou re-busca se faltarem evidências.
4. **Orquestrar agentes via LangChain**, usando o padrão do projeto (ex.: **supervisor → recuperador → verificador de segurança → redator com citações**).
5. Incluir **uma rotina de automação** (workflow agentic) além do Q&A: o agente deve executar pelo menos **1 processo** (ver seção “Automação”).
6. **Usar MCP (Model Context Protocol)** para integrar ao menos **1 ferramenta externa** (servidor MCP próprio ou de terceiros).

---

### Requisitos técnicos mínimos (stack)

**Stack base:** Python, LangChain + LangGraph, FAISS ou Chroma (evitar SaaS pago), UI Next.js, código no GitHub.

#### LLM (preferência local)
* Preferência: **Ollama** com LLMs open-source (ex.: Llama 3.x, Qwen2.5, Mistral/Gemma, etc.). ([ollama.com](https://ollama.com/library?utm_source=chatgpt.com))

#### Embeddings (OSS)
* HuggingFace embeddings (ex.: **bge-m3** ou gte/bge-*small*). ([huggingface.co](https://huggingface.co/BAAI/bge-m3?utm_source=chatgpt.com))

---

### Agentes 

#### Núcleo RAG (obrigatório)

1. **Supervisor (router de intents):** Decide se precisa buscar; escolhe rota (Q&A, automação, ou recusa).
2. **Retriever-agent:** Chunking + busca densa (FAISS/Chroma); **rerank opcional** (bônus).
3. **Safety/Policy:** Adiciona disclaimer para saúde/leis; evita aconselhamento perigoso.
4. **Answerer/Writer (com citações obrigatórias):** Resposta formatada com fontes e trechos.
5. **Self-check (estilo Self-RAG):** Valida se as afirmações estão suportadas por evidências recuperadas. Se falhar: re-busca (1 tentativa) ou recusa.

> Para Self-RAG local com LangGraph, há tutorial oficial. ([langchain-ai.github.io](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_self_rag_local/?utm_source=chatgpt.com))

#### Automação 

Adicionar uma rota **AUTOMAÇÃO** com um “Automation Agent” (pode ser um subagent):

* **Automation Agent (executa um processo com ferramentas):** Ex.: classificar/triagem, preencher templates, gerar checklist, elaborar relatório, extrair ações, etc. Pode usar RAG como “consulta de norma/guia” ao longo do processo.

---

### MCP (Model Context Protocol) — obrigatório

Vocês devem integrar **pelo menos 1 MCP server** como ferramenta do agente (via adapters), em uma destas opções:

#### Opção 1 — MCP próprio 
Criar um MCP simples local, por exemplo:

* `mcp-docstore`: expõe o corpus (ou metadados) como ferramenta padronizada
* `mcp-checklist`: gera/valida checklists de conformidade (WCAG, regras de processo, etc.)
* `mcp-files`: interface controlada para leitura/escrita em pasta do projeto (com allowlist)

#### Opção 2 — MCP “da Web” (terceiros)
Usar um servidor MCP já existente (por exemplo, diretórios de servidores MCP) e integrá-lo como ferramenta do agente. Referências de listagem:

* Coleção de servidores MCP (repo). ([github.com](https://github.com/modelcontextprotocol/servers?utm_source=chatgpt.com))
* Listas curadas de MCP servers. ([mcpservers.org](https://mcpservers.org/?utm_source=chatgpt.com))
* Exemplos oficiais. ([modelcontextprotocol.io](https://modelcontextprotocol.io/examples?utm_source=chatgpt.com))
* Doc do LangChain para MCP + adapters. ([docs.langchain.com](https://docs.langchain.com/oss/python/langchain/mcp?utm_source=chatgpt.com))

#### Segurança (obrigatório no README)
Como MCP é “plugar ferramentas”, exigir:

* **allowlist** de comandos/funções
* limitar acesso a arquivos/pastas
* registrar chamadas de tool
* justificar a escolha do MCP (e riscos). Há incidentes reais de risco com servidores MCP (supply-chain / exfiltração), então isso entra como item de maturidade e responsabilidade.

---

### Trilhas e ideias de PoC (escolha 1) — mantendo as suas

As trilhas originais continuam, só acrescento um “gancho de automação” em cada uma:

#### Saúde
* “Guia SUS” (Q&A com citações)
* **Automação sugerida**: “triagem de dúvidas” → classifica tema (vacina, atenção básica, etc.) → responde com fontes → inclui disclaimer

#### Educação
* “Assistente do Estudante” (regulamentos/ementas/FAQ). **Pode usar a API Eureca aqui. Bônus para quem fizer.**
* **Automação sugerida**: “planejador de matrícula” baseado em regras públicas (sem dados pessoais) + citações das normas

#### Meio ambiente
* “Clima em Foco” (IPCC AR6)
* **Automação sugerida**: “gerador de brief semanal” (a partir de um conjunto fixo de docs baixados) + log de mudanças

#### Inclusão digital
* “Acessibilidade Web” (WCAG 2.2)
* **Automação sugerida**: “auditoria/checklist” de uma página de exemplo (ou HTML local) → recomendações com trechos normativos

#### Justiça social
* “Direitos em Foco” (cartilhas/defensorias)
* **Automação sugerida**: “encaminhador” → identifica tipo de necessidade → sugere canais oficiais → sempre com disclaimer

---

### Avaliação (obrigatória no README)

Manter o que você tinha e adicionar 2 itens leves de automação/MCP:

#### RAG (como você propôs)
* 10–20 perguntas rotuladas + RAGAS/Giskard
* Métricas: Context Precision/Recall, Faithfulness, Answer Relevancy, latência

RAGAS (métricas). ([docs.ragas.io](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/?utm_source=chatgpt.com))

#### Automação (novo, mínimo viável)
* Definir **5 tarefas** de automação (inputs + output esperado)
* Medir: taxa de sucesso, nº médio de steps, tempo médio

#### MCP (novo, mínimo viável)
* Documentar o MCP usado (ou construído), endpoints/tools expostos
* Explicar controles: allowlist, limites, logs, e “o que o agente não pode fazer”

---

### Entregáveis (iguais aos seus)
* GitHub (MIT/Apache-2.0) com README, src/, app/, ingest/, eval/, tests/, Dockerfile, LICENSE, CITATION.cff
* Demo (Next.js + FastAPI local ou Docker)
* Slides (5–10): problema → público-alvo → arquitetura (grafo) → demo → métricas → limitações/próximos passos

---

### Materiais adicionais 
* Deep Agents overview/quickstart. ([docs.langchain.com](https://docs.langchain.com/oss/python/deepagents/quickstart?utm_source=chatgpt.com))
* Template “RAG Research Agent” (base pronta). ([github.com](https://github.com/langchain-ai/rag-research-agent-template?utm_source=chatgpt.com))
* MCP no LangChain (como plugar ferramentas via MCP). ([docs.langchain.com](https://docs.langchain.com/oss/python/langchain/mcp?utm_source=chatgpt.com))
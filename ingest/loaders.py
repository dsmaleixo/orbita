"""Document loaders for PDF and HTML sources."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import requests
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

_TIMEOUT = 30  # seconds for HTTP requests


def load_pdf(url_or_path: str, title: str, source_id: str) -> List[Document]:
    """Load a PDF from a URL or local path and return LangChain Documents."""
    try:
        from pypdf import PdfReader
        import io

        if url_or_path.startswith("http"):
            logger.info("Downloading PDF: %s", url_or_path)
            response = requests.get(url_or_path, timeout=_TIMEOUT)
            response.raise_for_status()
            reader = PdfReader(io.BytesIO(response.content))
        else:
            reader = PdfReader(url_or_path)

        docs = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if not text:
                continue
            docs.append(
                Document(
                    page_content=text,
                    metadata={
                        "source_id": source_id,
                        "source_url": url_or_path,
                        "title": title,
                        "page_number": page_num,
                        "doc_type": "pdf",
                        "language": "pt",
                    },
                )
            )
        logger.info("Loaded %d pages from PDF: %s", len(docs), title)
        return docs

    except Exception as exc:
        logger.warning("Failed to load PDF %s: %s", url_or_path, exc)
        return []


def load_html(url: str, title: str, source_id: str) -> List[Document]:
    """Load and parse an HTML page, returning text as LangChain Documents."""
    try:
        from bs4 import BeautifulSoup

        logger.info("Fetching HTML: %s", url)
        response = requests.get(url, timeout=_TIMEOUT, headers={"User-Agent": "OrbeitaBot/0.1"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script/style tags
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extract meaningful text blocks
        paragraphs = soup.find_all(["p", "h1", "h2", "h3", "h4", "li"])
        text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        if not text:
            return []

        return [
            Document(
                page_content=text,
                metadata={
                    "source_id": source_id,
                    "source_url": url,
                    "title": title,
                    "page_number": 1,
                    "doc_type": "html",
                    "language": "pt",
                },
            )
        ]

    except Exception as exc:
        logger.warning("Failed to load HTML %s: %s", url, exc)
        return []


def load_synthetic_corpus() -> List[Document]:
    """Return synthetic financial education documents for demo/testing.

    These documents cover core Brazilian financial literacy topics and are
    used as fallback when real URLs are unavailable (e.g., in CI/offline).
    """
    SYNTHETIC_DOCS = [
        {
            "title": "Tesouro Direto - Guia Básico",
            "source_id": "synthetic_tesouro",
            "source_url": "https://www.tesourodireto.com.br/",
            "content": """O Tesouro Direto é um programa do Tesouro Nacional desenvolvido em parceria com a
B3 para venda de títulos públicos federais para pessoas físicas, de forma 100% online.
Os títulos disponíveis são: Tesouro Selic (LFT), Tesouro Prefixado (LTN e NTN-F), e
Tesouro IPCA+ (NTN-B Principal e NTN-B). O Tesouro Selic acompanha a taxa básica de
juros (Selic), sendo indicado para reserva de emergência. O Tesouro IPCA+ garante
rendimento acima da inflação. O investimento mínimo é de R$30,00. Os títulos são
garantidos pelo Tesouro Nacional, com risco quase zero de calote.""",
        },
        {
            "title": "Poupança - Funcionamento e Rendimento",
            "source_id": "synthetic_poupanca",
            "source_url": "https://www.bcb.gov.br/cidadaniafinanceira/poupanca",
            "content": """A caderneta de poupança é um dos investimentos mais populares no Brasil, com
liquidez diária e isenção de Imposto de Renda para pessoas físicas. O rendimento da
poupança é calculado pela regra: quando a taxa Selic estiver acima de 8,5% ao ano, a
poupança rende 0,5% ao mês + TR (Taxa Referencial). Quando a Selic for igual ou inferior
a 8,5% ao ano, a poupança rende 70% da Selic + TR. A poupança tem cobertura do FGC
(Fundo Garantidor de Créditos) de até R$250.000 por instituição.""",
        },
        {
            "title": "CDI e Renda Fixa - Conceitos Fundamentais",
            "source_id": "synthetic_cdi",
            "source_url": "https://www.bcb.gov.br/cidadaniafinanceira/cdi",
            "content": """O CDI (Certificado de Depósito Interbancário) é uma taxa de referência para
investimentos de renda fixa no Brasil. O CDI é muito próximo da taxa Selic. Investimentos
como CDB (Certificado de Depósito Bancário), LCI (Letra de Crédito Imobiliário) e LCA
(Letra de Crédito do Agronegócio) costumam ter rendimento expresso como percentual do CDI.
Por exemplo, um CDB que rende 100% do CDI acompanha a taxa básica. LCI e LCA são isentos
de IR para pessoas físicas. O FGC cobre até R$250.000 por instituição financeira e R$1 milhão
por CPF para esses produtos.""",
        },
        {
            "title": "FGTS - Fundo de Garantia por Tempo de Serviço",
            "source_id": "synthetic_fgts",
            "source_url": "https://www.caixa.gov.br/trabalhador/fgts",
            "content": """O FGTS é um fundo criado para proteger o trabalhador demitido sem justa causa.
Todo empregador é obrigado a depositar mensalmente 8% do salário do funcionário em uma
conta vinculada na Caixa Econômica Federal. O FGTS pode ser sacado nos seguintes casos:
demissão sem justa causa, aposentadoria, compra de imóvel, financiamento pelo SFH,
doenças graves (câncer, HIV), calamidade pública, ou aniversário (saque-aniversário).
O FGTS rende 3% ao ano + TR, mais um complemento de resultados. O saldo pode ser
consultado pelo aplicativo FGTS da Caixa.""",
        },
        {
            "title": "Seguro-Desemprego - Requisitos e Benefícios",
            "source_id": "synthetic_seguro_desemprego",
            "source_url": "https://www.gov.br/trabalho-e-previdencia/seguro-desemprego",
            "content": """O seguro-desemprego é um benefício que oferece assistência financeira temporária
ao trabalhador desempregado em virtude de dispensa sem justa causa. Para ter direito, o
trabalhador precisa: ter sido demitido sem justa causa, não possuir renda própria suficiente,
e ter trabalhado por período mínimo (12 meses nos últimos 18 meses na 1ª solicitação, 9 meses
nos últimos 12 meses na 2ª solicitação, e 6 meses nos últimos 6 meses nas demais). O valor
varia de 1 a 2 salários mínimos, dependendo do salário médio dos últimos 3 meses.""",
        },
        {
            "title": "Planejamento Financeiro Pessoal",
            "source_id": "synthetic_planejamento",
            "source_url": "https://www.bcb.gov.br/cidadaniafinanceira/planejamento",
            "content": """O planejamento financeiro pessoal começa com o controle do orçamento mensal.
O método 50/30/20 sugere destinar 50% da renda para necessidades básicas (moradia, alimentação,
transporte), 30% para desejos pessoais (lazer, entretenimento), e 20% para poupança e
investimentos. A reserva de emergência deve cobrir entre 3 e 6 meses de despesas mensais,
mantida em investimentos de alta liquidez como Tesouro Selic ou CDB com liquidez diária.
Dívidas de alto custo (cartão de crédito: média 400% ao ano, cheque especial: média 150% ao ano)
devem ser priorizadas no pagamento antes de iniciar investimentos.""",
        },
        {
            "title": "Cartão de Crédito - Uso Consciente",
            "source_id": "synthetic_cartao",
            "source_url": "https://www.bcb.gov.br/cidadaniafinanceira/cartao",
            "content": """O cartão de crédito é uma ferramenta útil quando usado corretamente. A fatura
deve ser paga integralmente todo mês para evitar os juros rotativos, que são os maiores do
mercado financeiro brasileiro (média de 400% ao ano). O limite do cartão não deve ser
considerado como parte da renda disponível. O pagamento mínimo da fatura gera dívida
crescente. Antes de parcelar compras, verifique se há cobrança de juros. Cashback e milhas
são benefícios apenas quando a fatura é paga em dia.""",
        },
        {
            "title": "Previdência Privada - PGBL e VGBL",
            "source_id": "synthetic_previdencia",
            "source_url": "https://www.susep.gov.br/previdencia",
            "content": """A previdência privada complementa a previdência social (INSS). Os dois principais
produtos são o PGBL (Plano Gerador de Benefício Livre) e o VGBL (Vida Gerador de Benefício
Livre). O PGBL permite deduzir até 12% da renda bruta no IR (indicado para quem faz a
declaração completa). O VGBL não tem dedução fiscal na entrada, mas o IR incide apenas
sobre os rendimentos no resgate. Existem dois regimes tributários: progressivo (alíquotas
de 0% a 27,5%) e regressivo (alíquotas de 35% a 10%, reduzindo com o tempo de aplicação).
Taxas de administração e carregamento devem ser avaliadas antes da contratação.""",
        },
        {
            "title": "Educação Financeira para Jovens",
            "source_id": "synthetic_jovens",
            "source_url": "https://www.bcb.gov.br/cidadaniafinanceira/jovens",
            "content": """Para os jovens brasileiros, começar a poupar cedo faz uma grande diferença devido
aos juros compostos. Uma pessoa que começa a investir R$200/mês aos 20 anos terá muito mais
do que quem começa aos 30 anos, mesmo aplicando o dobro. O primeiro passo é criar uma reserva
de emergência antes de pensar em investimentos de maior risco. O INSS é obrigatório para
trabalhadores com carteira assinada (alíquotas de 7,5% a 14% sobre o salário). O programa
Desenrola Brasil ajuda trabalhadores com dívidas a renegociar condições mais favoráveis.
Jovens devem evitar dívidas desnecessárias no início da carreira.""",
        },
        {
            "title": "Fundos de Investimento - Conceitos Básicos",
            "source_id": "synthetic_fundos",
            "source_url": "https://www.cvm.gov.br/investidor/fundos",
            "content": """Fundos de investimento são condomínios de investidores que reúnem recursos para
aplicação em conjunto. Os tipos mais comuns são: Fundos de Renda Fixa (DI, crédito privado),
Fundos Multimercado (diversificados), Fundos de Ações, e Fundos Imobiliários (FIIs). As
taxas cobradas incluem taxa de administração (anual, incide sobre o patrimônio) e taxa de
performance (sobre rentabilidade acima do benchmark). A cota é o valor unitário do fundo.
O come-cotas é uma antecipação semestral de IR em fundos abertos. FIIs distribuem rendimentos
mensais isentos de IR para pessoas físicas com menos de 10% das cotas do fundo.""",
        },
    ]

    docs = []
    for item in SYNTHETIC_DOCS:
        docs.append(
            Document(
                page_content=item["content"],
                metadata={
                    "source_id": item["source_id"],
                    "source_url": item["source_url"],
                    "title": item["title"],
                    "page_number": 1,
                    "doc_type": "synthetic",
                    "language": "pt",
                },
            )
        )
    return docs

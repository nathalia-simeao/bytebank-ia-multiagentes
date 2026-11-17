"""Leitura, classificação, controle de acesso e fragmentação de políticas fictícias."""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "politicas_bytebank.csv"
ACCESS_LEVELS = {"publico": 0, "interno": 1, "restrito": 2}
DOMAINS = {"conta_corrente", "cartao_credito", "suporte", "rh", "seguranca"}


@dataclass(frozen=True)
class Policy:
    id: int
    dominio: str
    secao: str
    conteudo: str
    nivel_acesso: str


@dataclass(frozen=True)
class Chunk:
    text: str
    metadata: dict[str, str | int]


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in value if not unicodedata.combining(c))


def keywords(text: str) -> set[str]:
    stops = {"qual", "como", "para", "que", "uma", "com", "por", "pelo", "pela", "sobre", "tem", "meu", "minha", "posso", "esse", "essa", "sao", "dos", "das", "nos", "nas", "fazer", "quero", "preciso", "onde", "deve", "de", "do", "da", "em", "no", "na", "um", "ou", "os", "as", "ao", "e", "a", "o"}
    # Léxico pequeno e explicável para o fallback offline; não substitui embeddings.
    aliases = {
        "perdido": "perda", "perdi": "perda", "roubado": "roubo",
        "bloquear": "bloqueio", "bloqueado": "bloqueio",
        "encerrar": "encerramento", "encerrada": "encerramento",
        "pedir": "solicitar", "pedido": "solicitacao",
    }
    return {aliases.get(t, t) for t in re.findall(r"[a-z0-9]+", normalize(text)) if len(t) > 2 and t not in stops}


def load_policies(path: Path = DATA) -> list[Policy]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    expected = {"id", "dominio", "secao", "conteudo", "nivel_acesso"}
    if not rows or any(not expected.issubset(r) for r in rows):
        raise ValueError("CSV vazio ou sem colunas de políticas obrigatórias")
    policies = []
    seen = set()
    for row in rows:
        if row["dominio"] not in DOMAINS or row["nivel_acesso"] not in ACCESS_LEVELS:
            raise ValueError(f"Domínio/perfil inválido na linha {row.get('id')}")
        policy_id = int(row["id"])
        if policy_id in seen or not row["conteudo"].strip():
            raise ValueError(f"Política duplicada/vazia: {policy_id}")
        seen.add(policy_id)
        policies.append(Policy(policy_id, row["dominio"], row["secao"], row["conteudo"], row["nivel_acesso"]))
    return policies


def can_access(policy_level: str, requester_level: str) -> bool:
    if requester_level not in ACCESS_LEVELS:
        raise ValueError("Perfil desconhecido: acesso negado")
    return ACCESS_LEVELS[policy_level] <= ACCESS_LEVELS[requester_level]


def categorize(text: str) -> str:
    words = keywords(text)
    if words & {"fraude", "seguranca", "autenticacao", "senha", "incidente"}:
        return "seguranca"
    if words & {"platinum", "cartao", "fatura", "limite", "anuidade"}:
        return "cartoes"
    if words & {"suporte", "reclamacao", "ouvidoria", "chamados"}:
        return "atendimento"
    if words & {"ferias", "colaboradores", "rh", "treinamento"}:
        return "pessoas"
    return "contas"


def split_text(text: str, size: int = 500, overlap: int = 100) -> list[str]:
    """Fallback offline que respeita bordas de palavras quando possível."""
    if not 0 <= overlap < size:
        raise ValueError("Use 0 <= overlap < size")
    out = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary
        out.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return out


def make_chunks(policies: list[Policy], size: int = 500, overlap: int = 100, langchain: bool = False) -> list[Chunk]:
    if langchain:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap, separators=["\n\n", "\n", ". ", " ", ""])
    chunks = []
    for policy in policies:
        parts = splitter.split_text(policy.conteudo) if langchain else split_text(policy.conteudo, size, overlap)
        for i, part in enumerate(parts):
            chunks.append(Chunk(part, {
                "id": policy.id, "dominio": policy.dominio, "secao": policy.secao,
                "nivel_acesso": policy.nivel_acesso, "categoria": categorize(policy.conteudo),
                "chunk_index": i,
            }))
    return chunks


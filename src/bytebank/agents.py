"""Supervisor e especialistas; protótipo LangGraph disponível opcionalmente."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Literal, TypedDict
from uuid import uuid4

from .policies import normalize
from .rag import RAGPipeline


Intent = Literal["conta_corrente", "cartao_credito", "suporte"]


def classify_intent(question: str, use_llm: bool = False) -> Intent:
    """Classificador offline determinístico; LLM pode assumir classificação quando habilitado."""
    if use_llm:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        output = ChatOpenAI(model=os.getenv("BYTEBANK_CHAT_MODEL", "gpt-4.1-mini"), temperature=0).invoke([
            SystemMessage(content=("Classifique a intenção em exatamente um token: conta_corrente, "
                                   "cartao_credito ou suporte. Não escreva explicações.")),
            HumanMessage(content=question),
        ]).content
        if str(output).strip() in {"conta_corrente", "cartao_credito", "suporte"}:
            return str(output).strip()  # type: ignore[return-value]
    q = normalize(question)
    if any(word in q for word in ("cartao", "fatura", "credito", "platinum", "anuidade", "limite")):
        return "cartao_credito"
    if any(word in q for word in ("conta", "pix", "tarifa", "portabilidade", "transferencia", "abertura", "salario")):
        return "conta_corrente"
    return "suporte"


def needs_human_approval(question: str) -> bool:
    q = normalize(question)
    return "platinum" in q and any(v in q for v in ("solicitar", "pedir", "quero", "aprovar", "aprovacao", "contratar"))


@dataclass
class AgentResponse:
    intent: Intent
    answer: str
    sources: list[dict]
    pending: bool = False
    request_id: str | None = None


class AgentCoordinator:
    """Versão simples, local e verificável para demonstração via CLI/testes."""

    def __init__(self, rag: RAGPipeline | None = None):
        self.rag = rag or RAGPipeline()
        self.pending: dict[str, AgentResponse] = {}

    def ask(self, question: str, access: str = "publico") -> AgentResponse:
        intent = classify_intent(question, use_llm=self.rag.llm)
        result = self.rag.ask(question, access)
        response = AgentResponse(intent, result.answer, result.sources)
        if intent == "cartao_credito" and needs_human_approval(question):
            response.pending = True
            response.request_id = str(uuid4())
            response.answer += "\n\n⏸️ Solicitação Platinum em análise humana. Nenhuma aprovação ou emissão foi realizada."
            self.pending[response.request_id] = response
        return response

    def decide(self, request_id: str, approved: bool) -> AgentResponse:
        if request_id not in self.pending:
            raise ValueError("Solicitação inexistente, concluída ou expirada")
        old = self.pending.pop(request_id)
        decision = "aprovada para fins de simulação" if approved else "recusada para fins de simulação"
        return AgentResponse(old.intent, old.answer + f"\n\nDecisão humana registrada: {decision}. Nenhuma transação real foi executada.", old.sources)


class GraphState(TypedDict, total=False):
    question: str
    access: str
    intent: Intent
    answer: str
    sources: list[dict]
    review_required: bool
    human_decision: str


def build_langgraph(rag: RAGPipeline | None = None):
    """StateGraph verdadeiro, com estado persistido em memória e interrupt/resume.

    Requer `pip install -e '.[agents]'`. A função não executa operações bancárias.
    """
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import END, START, StateGraph
    from langgraph.types import interrupt

    engine = rag or RAGPipeline()

    def supervisor(state: GraphState) -> GraphState:
        return {"intent": classify_intent(state["question"], use_llm=engine.llm)}

    def specialist(state: GraphState) -> GraphState:
        result = engine.ask(state["question"], state.get("access", "publico"))
        return {
            "answer": result.answer,
            "sources": result.sources,
            "review_required": state["intent"] == "cartao_credito" and needs_human_approval(state["question"]),
        }

    def human_review(state: GraphState) -> GraphState:
        # LangGraph suspende a execução antes de qualquer efeito de negócio.
        result = interrupt({
            "tipo": "aprovacao_platinum",
            "motivo": "Decisão humana obrigatória para solicitação Platinum fictícia",
            "pergunta": state["question"],
            "fontes": state.get("sources", []),
        })
        approved = bool(result.get("approved", False)) if isinstance(result, dict) else False
        decision = "aprovada para fins de demonstração" if approved else "recusada para fins de demonstração"
        return {"human_decision": decision, "answer": state["answer"] + f"\n\nDecisão humana: {decision}. Não houve operação bancária real."}

    def final(state: GraphState) -> GraphState:
        return {"answer": state.get("answer", "Encaminhado ao atendimento humano por falta de evidências.")}

    graph = StateGraph(GraphState)
    graph.add_node("supervisor", supervisor)
    for domain in ("conta_corrente", "cartao_credito", "suporte"):
        graph.add_node(domain, specialist)
    graph.add_node("aprovacao_humana", human_review)
    graph.add_node("resposta_final", final)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", lambda state: state["intent"], {
        "conta_corrente": "conta_corrente", "cartao_credito": "cartao_credito", "suporte": "suporte"
    })
    graph.add_edge("conta_corrente", "resposta_final")
    graph.add_edge("suporte", "resposta_final")
    graph.add_conditional_edges("cartao_credito", lambda s: "aprovacao_humana" if s.get("review_required") else "resposta_final", {
        "aprovacao_humana": "aprovacao_humana", "resposta_final": "resposta_final"
    })
    graph.add_edge("aprovacao_humana", "resposta_final")
    graph.add_edge("resposta_final", END)
    return graph.compile(checkpointer=InMemorySaver())


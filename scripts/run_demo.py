"""CLI da demonstração sem credenciais por padrão."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bytebank.agents import AgentCoordinator  # noqa: E402
from bytebank.rag import RAGPipeline  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Bytebank fictício: RAG e agentes")
    parser.add_argument("--pergunta", default="Como abrir uma conta corrente?")
    parser.add_argument("--perfil", choices=["publico", "interno", "restrito"], default="publico")
    parser.add_argument("--vetorial", action="store_true", help="Ativa ChromaDB + OpenAI embeddings")
    parser.add_argument("--llm", action="store_true", help="Ativa OpenAI Chat para classificar e redigir")
    args = parser.parse_args()
    try:
        agent = AgentCoordinator(RAGPipeline(vector=args.vetorial, llm=args.llm))
        result = agent.ask(args.pergunta, args.perfil)
        print(f"Agente: {result.intent}\n\n{result.answer}")
        if result.pending:
            print(f"\nSolicitação de simulação pendente de revisão humana: {result.request_id}")
            print("Para testar a decisão, use a interface Gradio ou AgentCoordinator.decide().")
    except (RuntimeError, ImportError) as error:
        parser.exit(2, f"Configuração incompleta: {error}\n")


if __name__ == "__main__":
    main()


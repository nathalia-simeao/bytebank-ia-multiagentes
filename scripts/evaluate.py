"""Avaliação automatizada: recuperação de fonte e cobertura textual."""

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bytebank.policies import keywords  # noqa: E402
from bytebank.rag import RAGPipeline  # noqa: E402


def coverage(text: str, terms: str) -> float:
    expected = [word.strip() for word in terms.split("|") if word.strip()]
    text_words = keywords(text)
    return sum(bool(keywords(term) & text_words) for term in expected) / len(expected) if expected else 0.0


def evaluate(llm: bool = False):
    pipeline = RAGPipeline(llm=llm)
    with (ROOT / "data" / "validacao.csv").open(encoding="utf-8", newline="") as f:
        cases = list(csv.DictReader(f))
    rows = []
    for case in cases:
        result = pipeline.ask(case["pergunta"])
        ids = [s["id"] for s in result.sources]
        rows.append({
            "id": case["id"], "pergunta": case["pergunta"],
            "fonte_esperada": int(case["id_fonte"]),
            "fontes_recuperadas": ids,
            "hit_at_4": int(int(case["id_fonte"]) in ids),
            "cobertura_termos": round(coverage(result.answer, case["termos_esperados"]), 2),
            "resposta": result.answer,
        })
    hit_rate = sum(row["hit_at_4"] for row in rows) / len(rows)
    term_rate = sum(row["cobertura_termos"] for row in rows) / len(rows)
    return rows, hit_rate, term_rate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-llm", action="store_true", help="Compara com LLM externo usando API configurada")
    args = parser.parse_args()
    rows, hit_rate, term_rate = evaluate(llm=args.with_llm)
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    md = [
        "# Avaliação executada\n",
        f"Modo: {'RAG com LLM' if args.with_llm else 'Offline, lexical e extrativo'}  ",
        f"Casos: {len(rows)}  ",
        f"Hit@4: {hit_rate:.0%}  ",
        f"Cobertura média de termos (proxy): {term_rate:.0%}\n",
        "| Caso | Fonte esperada | Fontes retornadas | Hit@4 | Cobertura de termos |",
        "|---|---:|---|---:|---:|",
    ]
    for row in rows:
        md.append(f"| {row['id']} | {row['fonte_esperada']} | {row['fontes_recuperadas']} | {row['hit_at_4']} | {row['cobertura_termos']:.0%} |")
    md.extend(["", "**Atenção:** métricas automáticas não substituem revisão humana de correção factual, segurança, relevância e recusa apropriada."])
    output = results_dir / "avaliacao.md"
    output.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Hit@4: {hit_rate:.0%}; cobertura de termos: {term_rate:.0%}; relatório: {output}")


if __name__ == "__main__":
    main()


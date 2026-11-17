import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bytebank.agents import AgentCoordinator, classify_intent, needs_human_approval  # noqa: E402
from bytebank.rag import RAGPipeline  # noqa: E402


class TestAgents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = AgentCoordinator(RAGPipeline())

    def test_route(self):
        self.assertEqual(classify_intent("Qual é a tarifa da conta?"), "conta_corrente")
        self.assertEqual(classify_intent("Minha fatura do cartão venceu"), "cartao_credito")
        self.assertEqual(classify_intent("Quero abrir reclamação"), "suporte")

    def test_human_approval(self):
        self.assertTrue(needs_human_approval("Quero solicitar um cartão Platinum"))
        result = self.agent.ask("Quero solicitar cartão Platinum")
        self.assertTrue(result.pending)
        self.assertIsNotNone(result.request_id)
        decision = self.agent.decide(result.request_id, approved=False)
        self.assertIn("recusada para fins de simulação", decision.answer)
        with self.assertRaises(ValueError):
            self.agent.decide(result.request_id, approved=True)

    def test_unknown_query_avoids_invention(self):
        result = self.agent.ask("Como construir um foguete espacial?")
        self.assertIn("Não encontrei", result.answer)


class TestRAG(unittest.TestCase):
    def test_denies_internal_for_public(self):
        rag = RAGPipeline()
        result = rag.retrieve("política de férias dos colaboradores", access="publico")
        self.assertTrue(all(r["metadata"]["nivel_acesso"] == "publico" for r in result))
        self.assertNotIn(34, [r["metadata"]["id"] for r in result])

    def test_citations(self):
        result = RAGPipeline().ask("Como solicitar cartão Platinum?")
        self.assertTrue(result.grounded)
        self.assertIn(14, [s["id"] for s in result.sources])
        self.assertIn("[14]", result.answer)


if __name__ == "__main__":
    unittest.main()


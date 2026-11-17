import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bytebank.policies import can_access, load_policies, make_chunks, split_text  # noqa: E402


class TestPolicies(unittest.TestCase):
    def test_dataset_valid(self):
        policies = load_policies()
        self.assertEqual(len(policies), 50)
        self.assertEqual(len({p.id for p in policies}), 50)

    def test_access(self):
        self.assertFalse(can_access("restrito", "publico"))
        self.assertFalse(can_access("interno", "publico"))
        self.assertTrue(can_access("publico", "publico"))
        self.assertTrue(can_access("restrito", "restrito"))
        with self.assertRaises(ValueError):
            can_access("publico", "visitante_desconhecido")

    def test_chunks_have_metadata(self):
        chunks = make_chunks(load_policies())
        self.assertGreaterEqual(len(chunks), 50)
        for item in chunks:
            self.assertTrue({"id", "dominio", "secao", "nivel_acesso", "categoria"}.issubset(item.metadata))

    def test_chunking_overlap(self):
        parts = split_text("palavra " * 100, size=100, overlap=20)
        self.assertGreater(len(parts), 1)
        self.assertTrue(all(len(item) <= 100 for item in parts))


if __name__ == "__main__":
    unittest.main()


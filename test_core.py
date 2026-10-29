import unittest
from pathlib import Path

from corpus import NegationCorpus

DATA_PATH = Path(__file__).parent / "data" / "ossetic_negations_data.csv"


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = NegationCorpus(DATA_PATH)

    def test_corpus_size(self):
        self.assertEqual(len(self.corpus), 247)
        self.assertEqual(self.corpus.skipped_ids, [44])

    def test_questions_have_one_blank(self):
        for example in self.corpus.examples:
            with self.subTest(example_id=example.id):
                self.assertEqual(example.question_text().count("_____"), 1)
                self.assertNotIn("{", example.question_text())
                self.assertNotIn("}", example.question_text())

    def test_particle_counts(self):
        self.assertEqual(sum(self.corpus.particle_counts().values()), len(self.corpus))


if __name__ == "__main__":
    unittest.main()

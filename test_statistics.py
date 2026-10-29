import unittest
from pathlib import Path

from corpus import NegationCorpus
from models import NegationExample
from corpus_stats import CorpusStatistics, filter_examples


DATA = Path(__file__).parent / "data" / "ossetic_negations_data.csv"


class StatisticsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus = NegationCorpus(DATA)

    def test_totals(self):
        stats = CorpusStatistics(self.corpus.examples)

        self.assertEqual(len(stats), 247)

        self.assertEqual(
            stats.particle_counts(),
            {"ма": 118, "нӕ": 101, "не": 28},
        )

    def test_lengths_match_examples(self):
        stats = CorpusStatistics(self.corpus.examples)

        self.assertEqual(
            sum(map(len, stats.word_lengths().values())),
            247,
        )

        self.assertTrue(
            all(
                n > 0
                for v in stats.word_lengths().values()
                for n in v
            )
        )

    def test_word_count_ignores_punctuation(self):
        self.assertEqual(
            CorpusStatistics.word_count("Ма тӕрс!"),
            2,
        )

        self.assertEqual(
            CorpusStatistics.word_count("… — Ма тӕрс?"),
            2,
        )

    def test_filters_match_particle(self):
        filtered = filter_examples(
            self.corpus.examples,
            "",
            ["ма"],
            "Все источники",
        )

        self.assertEqual(len(filtered), 118)

    def test_filters_normalized_case(self):
        demo = NegationExample(
            id=99,
            raw_text="{Ма} тӕрс!",
            particle="ма",
            group="ma_negative",
            source="test",
        )

        self.assertEqual(
            filter_examples(
                [demo],
                "ТӔРС",
                ["ма"],
                "Все источники",
            ),
            [demo],
        )

    def test_filters_source(self):
        example = self.corpus.examples[0]

        filtered = filter_examples(
            self.corpus.examples,
            "",
            [example.particle],
            example.source,
        )

        self.assertTrue(filtered)

        self.assertTrue(
            all(
                e.source == example.source
                and e.particle == example.particle
                for e in filtered
            )
        )

    def test_empty_filter(self):
        self.assertEqual(
            filter_examples(
                self.corpus.examples,
                "",
                [],
                "Все источники",
            ),
            [],
        )

        self.assertEqual(
            CorpusStatistics([]).word_lengths(),
            {},
        )


if __name__ == "__main__":
    unittest.main()
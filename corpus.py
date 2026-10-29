import csv
import random
from collections import Counter
from pathlib import Path

from models import NegationExample


class NegationCorpus:
    def __init__(self, csv_path: str | Path):
        self.examples: list[NegationExample] = []
        self.skipped_ids: list[int] = []

        with open(csv_path, encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                example = NegationExample(
                    id=int(row["id"]),
                    raw_text=row["sentence_raw"],
                    particle=row["particle_form"],
                    group=row["particle_group"],
                    source=row["source_raw"],
                )
                if example.is_valid():
                    self.examples.append(example)
                else:
                    self.skipped_ids.append(example.id)

    def __len__(self) -> int:
        return len(self.examples)

    def particle_counts(self) -> Counter:
        return Counter(example.particle for example in self.examples)

    def get_questions(self, count: int = 10) -> list[NegationExample]:
        return random.sample(self.examples, k=min(count, len(self)))

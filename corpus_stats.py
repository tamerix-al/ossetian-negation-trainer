"""Описательная статистика корпуса. Не зависит от Streamlit и Plotly."""

from collections import Counter
import re
from typing import Iterable

from models import NegationExample, normalized


# Последовательности букв (без цифр и подчёркивания).
# Подходит для приближённого подсчёта слов
# в осетинском тексте на кириллице.
WORD = re.compile(r"[^\W\d_]+", flags=re.UNICODE)


class CorpusStatistics:
    """Вычисляет показатели по выбранной части корпуса."""

    def __init__(self, examples: Iterable[NegationExample]):
        self.examples = list(examples)

    def __len__(self) -> int:
        return len(self.examples)

    def particle_counts(self) -> Counter[str]:
        """Число размеченных вхождений по форме частицы."""
        return Counter(
            example.particle.casefold()
            for example in self.examples
        )

    @staticmethod
    def word_count(text: str) -> int:
        """Приблизительное количество слов; пунктуация не учитывается."""
        return len(WORD.findall(text))

    def word_lengths(self) -> dict[str, list[int]]:
        """Длины предложений с целевой частицей по форме частицы."""
        lengths: dict[str, list[int]] = {}

        for example in self.examples:
            lengths.setdefault(
                example.particle.casefold(), []
            ).append(
                self.word_count(example.answer_text())
            )

        return lengths


def filter_examples(
    examples: list[NegationExample],
    text_query: str,
    particles: list[str],
    source: str,
) -> list[NegationExample]:
    """Поиск без учёта регистра и фильтры для корпуса и графиков."""

    query = normalized(text_query.strip())

    return [
        example
        for example in examples
        if example.particle in particles
        and (
            source == "Все источники"
            or example.source == source
        )
        and (
            not query
            or query in normalized(example.full_text())
        )
    ]
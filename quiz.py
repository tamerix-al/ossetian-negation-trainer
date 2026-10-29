"""Логика тренажёра. Не зависит от консоли или Streamlit."""

import random

from corpus import NegationCorpus
from models import NegationExample


class QuizSession:
    MAX_QUESTION_LENGTH = 200  # keep the trainer focused on short excerpts

    OPTIONS = {
        "ma_negative": "ма",
        "standard_negative": "нӕ / не",
    }

    def __init__(
        self,
        corpus: NegationCorpus,
        question_count: int = 10,
        seed: int | None = None,
    ):
        if question_count < 1:
            raise ValueError("В тесте должен быть хотя бы один вопрос")
        if len(corpus) == 0:
            raise ValueError("В корпусе нет доступных примеров")

        # Full excerpts remain in the corpus; very long single sentences are
        # omitted from the trainer to keep the questions readable.
        eligible = [
            item for item in corpus.examples
            if len(item.question_text()) <= self.MAX_QUESTION_LENGTH
        ]
        if not eligible:
            raise ValueError("В корпусе нет достаточно коротких заданий")

        # Один вопрос — одно вхождение частицы из корпуса.
        self.questions = random.Random(seed).sample(
            eligible, k=min(question_count, len(eligible))
        )
        self.answers: list[dict] = []

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def answered(self) -> int:
        return len(self.answers)

    @property
    def score(self) -> int:
        return sum(item["is_correct"] for item in self.answers)

    @property
    def finished(self) -> bool:
        return self.answered == self.total

    @property
    def current_question(self) -> NegationExample | None:
        if self.finished:
            return None
        return self.questions[self.answered]

    def submit_answer(self, selected_group: str) -> bool:
        if self.finished:
            raise RuntimeError("Все вопросы уже пройдены")
        if selected_group not in self.OPTIONS:
            raise ValueError("Неизвестный вариант ответа")

        question = self.current_question
        assert question is not None
        is_correct = selected_group == question.group
        self.answers.append(
            {
                "example_id": question.id,
                "selected_group": selected_group,
                "correct_group": question.group,
                "is_correct": is_correct,
            }
        )
        return is_correct

"""Консольная проверка тренажёра перед разработкой веб-интерфейса."""

from pathlib import Path

from corpus import NegationCorpus
from quiz import QuizSession

DATA_PATH = Path(__file__).parent / "data" / "ossetic_negations_data.csv"


def main() -> None:
    corpus = NegationCorpus(DATA_PATH)
    print(f"Загружено примеров: {len(corpus)}")
    print(f"Пропущены строки: {corpus.skipped_ids}")

    quiz = QuizSession(corpus, question_count=10)
    print("\nТренажёр «Ма или нӕ?»")
    print("Для выхода введите q.\n")

    while not quiz.finished:
        question = quiz.current_question
        assert question is not None
        print(f"\nВопрос {quiz.answered + 1} из {quiz.total}")
        print(question.question_text())
        print("1 — ма   2 — нӕ / не")

        selected = input("Ваш ответ: ").strip().lower()
        if selected == "q":
            break
        if selected not in {"1", "2"}:
            print("Введите 1, 2 или q.")
            continue

        selected_group = "ma_negative" if selected == "1" else "standard_negative"
        is_correct = quiz.submit_answer(selected_group)
        print("Верно!" if is_correct else "Не совпало с корпусным примером.")
        print("В оригинале:", question.full_text())
        print("Частица:", question.particle)

    print(f"\nРезультат: {quiz.score} из {quiz.answered}")
    if quiz.answered:
        print(f"Правильных ответов: {quiz.score / quiz.answered:.0%}")


if __name__ == "__main__":
    main()

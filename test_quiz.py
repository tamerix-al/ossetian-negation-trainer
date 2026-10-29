import unittest
from pathlib import Path

from corpus import NegationCorpus
from quiz import QuizSession

DATA_PATH = Path(__file__).parent / "data" / "ossetic_negations_data.csv"


class QuizTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = NegationCorpus(DATA_PATH)

    def test_questions_have_unique_ids(self):
        quiz = QuizSession(self.corpus, question_count=10, seed=1)
        self.assertEqual(quiz.total, 10)
        self.assertEqual(len({q.id for q in quiz.questions}), 10)

    def test_same_seed_gives_same_questions(self):
        a = QuizSession(self.corpus, seed=42)
        b = QuizSession(self.corpus, seed=42)
        self.assertEqual([q.id for q in a.questions], [q.id for q in b.questions])

    def test_correct_answer_and_finished(self):
        quiz = QuizSession(self.corpus, question_count=1, seed=1)
        question = quiz.current_question
        self.assertIsNotNone(question)
        self.assertTrue(quiz.submit_answer(question.group))
        self.assertEqual(quiz.score, 1)
        self.assertEqual(quiz.answered, 1)
        self.assertTrue(quiz.finished)
        self.assertIsNone(quiz.current_question)
        with self.assertRaises(RuntimeError):
            quiz.submit_answer(question.group)

    def test_wrong_answer(self):
        quiz = QuizSession(self.corpus, question_count=1, seed=1)
        correct = quiz.current_question.group
        wrong = "standard_negative" if correct == "ma_negative" else "ma_negative"
        self.assertFalse(quiz.submit_answer(wrong))
        self.assertEqual(quiz.score, 0)

    def test_invalid_answer_does_not_advance(self):
        quiz = QuizSession(self.corpus, question_count=2, seed=1)
        with self.assertRaises(ValueError):
            quiz.submit_answer("incorrect_option")
        self.assertEqual(quiz.answered, 0)

    def test_invalid_size(self):
        with self.assertRaises(ValueError):
            QuizSession(self.corpus, question_count=0)

    def test_large_size_is_limited_by_eligible_questions(self):
        eligible_ids = {
            example.id
            for example in self.corpus.examples
            if len(example.question_text()) <= QuizSession.MAX_QUESTION_LENGTH
        }

        quiz = QuizSession(
            self.corpus,
            question_count=len(self.corpus) + 1,
            seed=1,
        )

        self.assertEqual(quiz.total, len(eligible_ids))
        self.assertEqual(
            {question.id for question in quiz.questions},
            eligible_ids,
        )


if __name__ == "__main__":
    unittest.main()

"""Веб-приложение: тренажёр, корпусный поиск и описательная статистика."""

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from corpus import NegationCorpus
from models import NegationExample
from quiz import QuizSession
from corpus_stats import CorpusStatistics, filter_examples


DATA_PATH = Path(__file__).resolve().parent / "data" / "ossetic_negations_data.csv"
PARTICLE_ORDER = ("ма", "нӕ", "не")


@st.cache_resource(show_spinner=False)
def load_corpus() -> NegationCorpus:
    """Один раз загружаем данные; приложение не изменяет CSV."""
    return NegationCorpus(DATA_PATH)


def start_quiz(corpus: NegationCorpus, question_count: int) -> None:
    """Начинаем тест и сбрасываем состояние интерфейса."""
    st.session_state.quiz = QuizSession(corpus, question_count=question_count)
    st.session_state.feedback = None
    st.session_state.round_id = st.session_state.get("round_id", 0) + 1


def render_quiz(corpus: NegationCorpus, question_count: int) -> None:
    if "quiz" not in st.session_state:
        start_quiz(corpus, question_count)

    quiz: QuizSession = st.session_state.quiz
    feedback: dict | None = st.session_state.feedback

    st.progress(quiz.answered / quiz.total)
    left, right = st.columns(2)
    left.metric("Отвечено", f"{quiz.answered} / {quiz.total}")
    right.metric("Совпадений", str(quiz.score))

    if quiz.finished and feedback is None:
        st.subheader("Результат теста")
        st.success(
            f"{quiz.score} из {quiz.total} — "
            f"{quiz.score / quiz.total:.0%} совпадений с корпусом"
        )
        st.write(
            "Правильным считался вариант, который встречался "
            "в исходном примере."
        )

        if st.button(
            "Пройти ещё раз",
            type="primary",
            use_container_width=True,
        ):
            start_quiz(corpus, question_count)
            st.rerun()
        return

    question = (
        quiz.current_question
        if feedback is None
        else feedback["question"]
    )
    assert question is not None

    number = quiz.answered if feedback else quiz.answered + 1
    st.subheader(f"Вопрос {number} из {quiz.total}")

    with st.container(border=True):
        st.markdown(
            "**Какую частицу нужно поставить вместо пропуска?**"
        )
        st.markdown(f"### {question.question_text()}")

    if feedback is None:
        selection = st.radio(
            "Выбери вариант",
            options=list(QuizSession.OPTIONS),
            format_func=lambda group: QuizSession.OPTIONS[group],
            index=None,
            key=f"choice_{st.session_state.round_id}_{quiz.answered}",
        )

        if st.button(
            "Проверить",
            type="primary",
            disabled=selection is None,
            use_container_width=True,
        ):
            correct = quiz.submit_answer(selection)
            st.session_state.feedback = {
                "question": question,
                "is_correct": correct,
            }
            st.rerun()

    else:
        if feedback["is_correct"]:
            st.success("Совпало с исходным примером!")
        else:
            st.info(
                "В исходном примере использована другая группа частиц."
            )

        st.markdown(f"**В оригинале:** {question.answer_text()}")
        st.write(f"Частица: **{question.particle}**")

        with st.expander("Полный контекст и источник"):
            st.write(question.full_text())
            if question.source:
                st.caption(f"Источник: {question.source}")

        st.caption(
            "Ответ отражает реальное употребление в корпусе. "
            "Другой вариант не обязательно грамматически невозможен."
        )

        label = (
            "Показать результат"
            if quiz.finished
            else "Следующий вопрос"
        )

        if st.button(
            label,
            type="primary",
            use_container_width=True,
        ):
            st.session_state.feedback = None
            st.rerun()


def render_corpus(
    examples: list[NegationExample],
    total: int,
) -> None:
    st.subheader("Корпус предложений")
    st.caption(
        f"Подходят под фильтры: {len(examples)} из {total}. "
        "Фильтры находятся слева."
    )

    if not examples:
        st.info("По выбранным условиям примеров не найдено.")
        return

    rows = [
        {
            "ID": example.id,
            "Частица": example.particle,
            "Предложение": example.answer_text(),
            "Источник": example.source,
        }
        for example in examples
    ]

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    ids = [example.id for example in examples]

    chosen_id = st.selectbox(
        "Открыть полный контекст",
        options=ids,
        format_func=lambda i: f"Пример № {i}",
    )

    chosen = next(
        example
        for example in examples
        if example.id == chosen_id
    )

    with st.container(border=True):
        st.write(chosen.full_text())
        st.caption(
            f"Частица: {chosen.particle} | ID: {chosen.id}"
        )

        if chosen.source:
            st.caption(f"Источник: {chosen.source}")


def render_statistics(
    examples: list[NegationExample],
    total: int,
) -> None:
    st.subheader("Статистика корпуса")
    st.caption(
        f"Графики построены по {len(examples)} из {total} "
        "примеров с учётом фильтров слева."
    )

    st.info(
        "Датасет содержит специально отобранные предложения. "
        "Графики описывают эту коллекцию, а не частотность "
        "частиц в осетинском языке."
    )

    if not examples:
        st.warning("Нет данных для визуализации. Измени фильтры.")
        return

    stats = CorpusStatistics(examples)

    # График 1: количество вхождений частиц
    counts = stats.particle_counts()
    shown = [
        p for p in PARTICLE_ORDER
        if counts.get(p, 0)
    ]

    fig_counts = go.Figure(
        data=[
            go.Bar(
                x=shown,
                y=[counts[p] for p in shown],
            )
        ]
    )

    fig_counts.update_layout(
        title="Количество размеченных вхождений",
        xaxis_title="Частица",
        yaxis_title="Примеров",
        margin=dict(l=20, r=20, t=55, b=20),
    )

    fig_counts.update_yaxes(rangemode="tozero")
    st.plotly_chart(fig_counts, use_container_width=True)

    # График 2: распределение длины предложений
    lengths = stats.word_lengths()

    fig_lengths = go.Figure()

    for particle in PARTICLE_ORDER:
        if particle in lengths:
            fig_lengths.add_trace(
                go.Box(
                    y=lengths[particle],
                    name=particle,
                    boxpoints="outliers",
                )
            )

    fig_lengths.update_layout(
        title="Длина предложения по форме частицы",
        xaxis_title="Частица",
        yaxis_title="Количество слов",
        showlegend=False,
        margin=dict(l=20, r=20, t=55, b=20),
    )

    st.plotly_chart(fig_lengths, use_container_width=True)

    st.caption(
        "Длина рассчитывается по одному предложению "
        "с целевой частицей, включая длинные предложения, "
        "исключённые из теста. Подсчёт слов приблизительный."
    )


def main() -> None:
    st.set_page_config(
        page_title="Ма или нӕ? — осетинский тренажёр",
        page_icon="📖",
        layout="wide",
    )

    st.title("Ма или нӕ?")
    st.write(
        "Тренажёр отрицательных частиц осетинского языка "
        "на основе корпусных примеров."
    )

    try:
        corpus = load_corpus()
    except (OSError, ValueError, KeyError) as exc:
        st.error(
            "Не удалось открыть корпус. "
            "Проверь data/ossetic_negations_data.csv."
        )
        st.exception(exc)
        st.stop()

    with st.sidebar:
        st.header("Тренажёр")

        question_count = st.selectbox(
            "Количество вопросов",
            [5, 10, 20],
            index=1,
        )

        if st.button(
            "Начать новый тест",
            use_container_width=True,
        ):
            start_quiz(corpus, question_count)
            st.rerun()

        st.caption(
            "Количество вопросов применяется "
            "при запуске нового теста."
        )

        st.divider()
        st.header("Фильтры корпуса и графиков")

        search = st.text_input(
            "Поиск по тексту",
            placeholder="Введи слово или сочетание",
        )

        chosen_particles = st.multiselect(
            "Частицы",
            options=list(PARTICLE_ORDER),
            default=list(PARTICLE_ORDER),
        )

        sources = sorted(
            set(
                e.source
                for e in corpus.examples
                if e.source
            )
        )

        source = st.selectbox(
            "Источник",
            options=["Все источники", *sources],
        )

        st.caption(
            f"В корпусе {len(corpus)} записей "
            "с формально корректной разметкой частицы."
        )

    selected = filter_examples(
        corpus.examples,
        search,
        chosen_particles,
        source,
    )

    tab_quiz, tab_corpus, tab_stats = st.tabs(
        ["Тренажёр", "Корпус", "Статистика"]
    )

    with tab_quiz:
        render_quiz(corpus, question_count)

    with tab_corpus:
        render_corpus(selected, len(corpus))

    with tab_stats:
        render_statistics(selected, len(corpus))


if __name__ == "__main__":
    main()
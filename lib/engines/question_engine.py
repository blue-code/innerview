"""질문 엔진 - JSON 기반 질문 로딩 및 흐름 제어"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..models.question import Question, QuestionCategory


DATA_DIR = Path(__file__).parent.parent / "data"


class QuestionEngine:
    """질문 세트를 로드하고 순서대로 제공하는 엔진"""

    def __init__(self, phase: int = 1):
        self.phase = phase
        self.questions: list[Question] = []
        self.current_index: int = 0
        self._load_questions()

    def _load_questions(self) -> None:
        path = DATA_DIR / "questions.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_questions = [Question(**q) for q in data["questions"]]
        self.questions = sorted(
            [q for q in all_questions if q.phase == self.phase],
            key=lambda q: q.order,
        )

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def progress(self) -> float:
        if self.total == 0:
            return 0.0
        return self.current_index / self.total

    @property
    def is_complete(self) -> bool:
        return self.current_index >= self.total

    def current_question(self) -> Optional[Question]:
        if self.is_complete:
            return None
        return self.questions[self.current_index]

    def answer(self, choice_index: int) -> dict[str, float]:
        """선택지를 선택하고 해당 점수를 반환"""
        question = self.current_question()
        if question is None:
            raise ValueError("모든 질문에 답변했습니다.")
        if choice_index < 0 or choice_index >= len(question.choices):
            raise ValueError(f"유효하지 않은 선택: {choice_index}")

        scores = question.choices[choice_index].scores
        self.current_index += 1
        return {dim.value if hasattr(dim, "value") else dim: score for dim, score in scores.items()}

    def get_questions_by_category(self, category: QuestionCategory) -> list[Question]:
        return [q for q in self.questions if q.category == category]

    def reset(self) -> None:
        self.current_index = 0

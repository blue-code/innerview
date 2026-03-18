"""질문 엔진 - JSON 기반 질문 로딩 및 흐름 제어"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Optional

from ..models.question import Question, QuestionCategory
from ..models.user_profile import RelationshipStatus


DATA_DIR = Path(__file__).parent.parent / "data"

# Phase 1에서 관계 질문 시작 전 삽입되는 분기 질문 ID 범위
RELATIONSHIP_QUESTION_IDS = {"R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10"}
COUPLE_QUESTION_IDS = {"P2_01", "P2_02", "P2_03", "P2_04", "P2_05", "P2_06", "P2_07", "P2_08", "P2_09", "P2_10"}


class QuestionEngine:
    """질문 세트를 로드하고 순서대로 제공하는 엔진"""

    def __init__(self, phase: int = 1, shuffle: bool = False, seed: Optional[int] = None,
                 relationship_status: RelationshipStatus = RelationshipStatus.PREFER_NOT_TO_SAY):
        self.phase = phase
        self.questions: list[Question] = []
        self.current_index: int = 0
        self.shuffle = shuffle
        self.seed = seed
        self.relationship_status = relationship_status
        self._load_questions()

    def _load_questions(self) -> None:
        path = DATA_DIR / "questions.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_questions = [Question(**q) for q in data["questions"]]

        # Phase 필터
        filtered = [q for q in all_questions if q.phase == self.phase]

        # Phase 분기: 싱글 유저는 커플 질문 제외
        if self.relationship_status == RelationshipStatus.SINGLE:
            filtered = [q for q in filtered if q.id not in COUPLE_QUESTION_IDS]

        # 정렬
        filtered = sorted(filtered, key=lambda q: q.order)

        # 카테고리 내 셔플 (스토리 큰 흐름은 유지하되 카테고리 내 순서는 랜덤)
        if self.shuffle:
            rng = random.Random(self.seed)
            by_cat: dict[str, list[Question]] = {}
            for q in filtered:
                by_cat.setdefault(q.category.value, []).append(q)
            for cat_qs in by_cat.values():
                rng.shuffle(cat_qs)
            # 카테고리 순서는 유지
            cat_order = ["emotion", "values", "behavior", "relationship", "experience"]
            result = []
            for cat in cat_order:
                result.extend(by_cat.get(cat, []))
            self.questions = result
        else:
            self.questions = filtered

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

    @property
    def current_category(self) -> Optional[str]:
        q = self.current_question()
        if q:
            return q.category.value
        return None

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

    def go_back(self) -> bool:
        """이전 질문으로 되돌아가기"""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False

    def get_questions_by_category(self, category: QuestionCategory) -> list[Question]:
        return [q for q in self.questions if q.category == category]

    def get_phase_intro(self) -> str:
        """현재 카테고리 변경 시 전환 내러티브"""
        cat = self.current_category
        intros = {
            "emotion": "여행의 첫 번째 장: 당신의 감정 숲",
            "values": "두 번째 장: 가치관의 오두막",
            "behavior": "세 번째 장: 행동의 마을",
            "relationship": "네 번째 장: 관계의 다리",
            "experience": "마지막 장: 기억의 호수",
        }
        return intros.get(cat, "")

    def reset(self) -> None:
        self.current_index = 0

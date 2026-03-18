"""스코어링 엔진 - Big Five / Attachment / Sternberg 점수 계산"""

from __future__ import annotations

from typing import Optional

from ..models.question import PsychDimension
from ..models.user_profile import (
    AttachmentProfile,
    BigFiveProfile,
    LoveTriangleProfile,
    RelationshipStatus,
    UserProfile,
)


# 사랑 삼각이론 차원별 가중치 (Phase 2 질문 부족 보정)
LOVE_WEIGHTS = {
    "intimacy": 1.0,
    "passion": 1.3,      # 질문 수 적으므로 가중치 보정
    "commitment": 1.4,   # 질문 수 적으므로 가중치 보정
}


class ScoringEngine:
    """답변 점수를 누적하고 프로파일을 생성"""

    def __init__(self):
        self.raw_scores: dict[str, float] = {}
        self.answer_count: dict[str, int] = {}

    def add_scores(self, scores: dict[str, float]) -> None:
        """한 질문의 답변 점수를 누적"""
        for dim, score in scores.items():
            dim_key = dim if isinstance(dim, str) else dim.value
            self.raw_scores[dim_key] = self.raw_scores.get(dim_key, 0) + score
            self.answer_count[dim_key] = self.answer_count.get(dim_key, 0) + 1

    def _normalize(self, dim_key: str, max_per_question: float = 10.0, weight: float = 1.0) -> float:
        """차원 점수를 0~100으로 정규화 (가중치 적용)"""
        count = self.answer_count.get(dim_key, 0)
        if count == 0:
            return 50.0
        raw = self.raw_scores.get(dim_key, 0)
        avg = raw / count
        weighted = avg * weight
        return min(100.0, max(0.0, (weighted / max_per_question) * 100))

    def get_confidence(self, dim_key: str) -> str:
        """해당 차원의 측정 신뢰도 (질문 수 기반)"""
        count = self.answer_count.get(dim_key, 0)
        if count >= 5:
            return "high"
        elif count >= 3:
            return "medium"
        elif count >= 1:
            return "low"
        return "none"

    def build_big_five(self) -> BigFiveProfile:
        return BigFiveProfile(
            extraversion=self._normalize("extraversion"),
            neuroticism=self._normalize("neuroticism"),
            conscientiousness=self._normalize("conscientiousness"),
            openness=self._normalize("openness"),
            agreeableness=self._normalize("agreeableness"),
        )

    def build_attachment(self) -> AttachmentProfile:
        return AttachmentProfile(
            secure=self._normalize("attachment_secure"),
            anxious=self._normalize("attachment_anxious"),
            avoidant=self._normalize("attachment_avoidant"),
        )

    def build_love_triangle(self) -> LoveTriangleProfile:
        return LoveTriangleProfile(
            intimacy=self._normalize("intimacy", weight=LOVE_WEIGHTS["intimacy"]),
            passion=self._normalize("passion", weight=LOVE_WEIGHTS["passion"]),
            commitment=self._normalize("commitment", weight=LOVE_WEIGHTS["commitment"]),
        )

    def build_profile(self, user_id: str, relationship_status: RelationshipStatus = RelationshipStatus.PREFER_NOT_TO_SAY) -> UserProfile:
        """전체 프로파일 생성"""
        return UserProfile(
            user_id=user_id,
            relationship_status=relationship_status,
            big_five=self.build_big_five(),
            attachment=self.build_attachment(),
            love_triangle=self.build_love_triangle(),
        )

    def get_all_confidences(self) -> dict[str, str]:
        """모든 차원의 신뢰도 반환"""
        dims = [
            "extraversion", "neuroticism", "conscientiousness", "openness", "agreeableness",
            "attachment_secure", "attachment_anxious", "attachment_avoidant",
            "intimacy", "passion", "commitment",
        ]
        return {d: self.get_confidence(d) for d in dims}

    def reset(self) -> None:
        self.raw_scores.clear()
        self.answer_count.clear()

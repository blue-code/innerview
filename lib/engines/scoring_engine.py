"""스코어링 엔진 - Big Five / Attachment / Sternberg 점수 계산"""

from __future__ import annotations

from ..models.question import PsychDimension
from ..models.user_profile import (
    AttachmentProfile,
    BigFiveProfile,
    LoveTriangleProfile,
    UserProfile,
)


# 각 차원별 최대 누적 가능 점수 (정규화 기준)
BIG_FIVE_DIMS = {
    PsychDimension.EXTRAVERSION,
    PsychDimension.NEUROTICISM,
    PsychDimension.CONSCIENTIOUSNESS,
    PsychDimension.OPENNESS,
    PsychDimension.AGREEABLENESS,
}

ATTACHMENT_DIMS = {
    PsychDimension.ATTACHMENT_SECURE,
    PsychDimension.ATTACHMENT_ANXIOUS,
    PsychDimension.ATTACHMENT_AVOIDANT,
}

LOVE_DIMS = {
    PsychDimension.INTIMACY,
    PsychDimension.PASSION,
    PsychDimension.COMMITMENT,
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

    def _normalize(self, dim_key: str, max_per_question: float = 10.0) -> float:
        """차원 점수를 0~100으로 정규화"""
        count = self.answer_count.get(dim_key, 0)
        if count == 0:
            return 50.0  # 기본값
        raw = self.raw_scores.get(dim_key, 0)
        avg = raw / count
        return min(100.0, max(0.0, (avg / max_per_question) * 100))

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
            intimacy=self._normalize("intimacy"),
            passion=self._normalize("passion"),
            commitment=self._normalize("commitment"),
        )

    def build_profile(self, user_id: str) -> UserProfile:
        """전체 프로파일 생성"""
        return UserProfile(
            user_id=user_id,
            big_five=self.build_big_five(),
            attachment=self.build_attachment(),
            love_triangle=self.build_love_triangle(),
        )

    def reset(self) -> None:
        self.raw_scores.clear()
        self.answer_count.clear()

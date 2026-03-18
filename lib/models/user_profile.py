"""사용자 심리 프로파일 모델"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .question import PsychDimension


class RelationshipStatus(str, Enum):
    """관계 상태"""
    SINGLE = "single"
    DATING = "dating"
    COMMITTED = "committed"
    MARRIED = "married"
    COMPLICATED = "complicated"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class BigFiveProfile(BaseModel):
    """Big Five 성격 프로파일 (각 0~100)"""
    extraversion: float = 50.0       # 외향성
    neuroticism: float = 50.0        # 신경성
    conscientiousness: float = 50.0  # 성실성
    openness: float = 50.0           # 개방성
    agreeableness: float = 50.0      # 친화성

    def level(self, trait: str) -> str:
        """점수를 높음/보통/낮음으로 변환"""
        val = getattr(self, trait, 50.0)
        if val >= 65:
            return "high"
        elif val <= 35:
            return "low"
        return "mid"


class AttachmentProfile(BaseModel):
    """애착 유형 프로파일 (스펙트럼 방식)"""
    secure: float = 50.0     # 안정형
    anxious: float = 50.0    # 불안형
    avoidant: float = 50.0   # 회피형

    @property
    def dominant_type(self) -> str:
        scores = {
            "안정형": self.secure,
            "불안형": self.anxious,
            "회피형": self.avoidant,
        }
        return max(scores, key=scores.get)

    @property
    def spectrum(self) -> dict[str, str]:
        """각 유형별 강도를 반환 (high/mid/low)"""
        def _level(v: float) -> str:
            if v >= 65:
                return "high"
            elif v <= 35:
                return "low"
            return "mid"
        return {
            "안정형": _level(self.secure),
            "불안형": _level(self.anxious),
            "회피형": _level(self.avoidant),
        }

    @property
    def is_mixed(self) -> bool:
        """두 유형 이상이 높은 경우"""
        high_count = sum(1 for v in [self.secure, self.anxious, self.avoidant] if v >= 55)
        return high_count >= 2

    @property
    def blend_description(self) -> str:
        """스펙트럼 기반 복합 유형 설명"""
        s = self.spectrum
        high_types = [k for k, v in s.items() if v == "high"]

        if len(high_types) == 0:
            return self.dominant_type
        elif len(high_types) == 1:
            return high_types[0]
        else:
            return " + ".join(high_types)

    @property
    def tension_pair(self) -> Optional[tuple[str, str]]:
        """심리적 긴장이 존재하는 유형 조합"""
        if self.anxious >= 55 and self.avoidant >= 55:
            return ("불안형", "회피형")
        if self.secure >= 55 and self.anxious >= 55:
            return ("안정형", "불안형")
        return None


class LoveTriangleProfile(BaseModel):
    """Sternberg 사랑의 삼각이론 프로파일"""
    intimacy: float = 50.0    # 친밀감
    passion: float = 50.0     # 열정
    commitment: float = 50.0  # 헌신

    @property
    def love_type(self) -> str:
        high_i = self.intimacy > 60
        high_p = self.passion > 60
        high_c = self.commitment > 60

        if high_i and high_p and high_c:
            return "완전한 사랑"
        elif high_i and high_p:
            return "낭만적 사랑"
        elif high_i and high_c:
            return "우애적 사랑"
        elif high_p and high_c:
            return "맹목적 사랑"
        elif high_i:
            return "좋아함"
        elif high_p:
            return "도취적 사랑"
        elif high_c:
            return "공허한 사랑"
        else:
            return "탐색 중"

    @property
    def strongest(self) -> str:
        scores = {"친밀감": self.intimacy, "열정": self.passion, "헌신": self.commitment}
        return max(scores, key=scores.get)

    @property
    def weakest(self) -> str:
        scores = {"친밀감": self.intimacy, "열정": self.passion, "헌신": self.commitment}
        return min(scores, key=scores.get)


class GrowthDelta(BaseModel):
    """이전 프로파일 대비 변화량"""
    dimension: str
    previous: float
    current: float
    delta: float
    direction: str  # "improved", "declined", "stable"
    message: str


class UserProfile(BaseModel):
    """사용자 전체 심리 프로파일"""
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    relationship_status: RelationshipStatus = RelationshipStatus.PREFER_NOT_TO_SAY
    big_five: BigFiveProfile = Field(default_factory=BigFiveProfile)
    attachment: AttachmentProfile = Field(default_factory=AttachmentProfile)
    love_triangle: LoveTriangleProfile = Field(default_factory=LoveTriangleProfile)
    answers: dict[str, int] = Field(default_factory=dict)

    def get_dimension_score(self, dimension: PsychDimension) -> float:
        mapping = {
            PsychDimension.EXTRAVERSION: self.big_five.extraversion,
            PsychDimension.NEUROTICISM: self.big_five.neuroticism,
            PsychDimension.CONSCIENTIOUSNESS: self.big_five.conscientiousness,
            PsychDimension.OPENNESS: self.big_five.openness,
            PsychDimension.AGREEABLENESS: self.big_five.agreeableness,
            PsychDimension.ATTACHMENT_SECURE: self.attachment.secure,
            PsychDimension.ATTACHMENT_ANXIOUS: self.attachment.anxious,
            PsychDimension.ATTACHMENT_AVOIDANT: self.attachment.avoidant,
            PsychDimension.INTIMACY: self.love_triangle.intimacy,
            PsychDimension.PASSION: self.love_triangle.passion,
            PsychDimension.COMMITMENT: self.love_triangle.commitment,
        }
        return mapping.get(dimension, 0.0)

    def compare_with(self, previous: UserProfile) -> list[GrowthDelta]:
        """이전 프로파일과 비교하여 성장/변화 추적"""
        deltas = []
        comparisons = [
            ("외향성", self.big_five.extraversion, previous.big_five.extraversion),
            ("신경성", self.big_five.neuroticism, previous.big_five.neuroticism),
            ("성실성", self.big_five.conscientiousness, previous.big_five.conscientiousness),
            ("개방성", self.big_five.openness, previous.big_five.openness),
            ("친화성", self.big_five.agreeableness, previous.big_five.agreeableness),
            ("안정 애착", self.attachment.secure, previous.attachment.secure),
            ("불안 애착", self.attachment.anxious, previous.attachment.anxious),
            ("회피 애착", self.attachment.avoidant, previous.attachment.avoidant),
        ]

        for name, curr, prev in comparisons:
            delta = curr - prev
            if abs(delta) < 3:
                direction = "stable"
                msg = f"{name}은 이전과 비슷합니다."
            elif delta > 0:
                positive_dims = {"외향성", "성실성", "개방성", "친화성", "안정 애착"}
                negative_dims = {"신경성", "불안 애착", "회피 애착"}
                if name in positive_dims:
                    direction = "improved"
                    msg = f"{name}이 {abs(delta):.0f}점 높아졌습니다."
                elif name in negative_dims:
                    direction = "declined"
                    msg = f"{name}이 {abs(delta):.0f}점 높아졌습니다. 스스로를 돌보는 시간이 필요할 수 있어요."
                else:
                    direction = "stable"
                    msg = f"{name}에 변화가 있습니다."
            else:
                negative_dims = {"신경성", "불안 애착", "회피 애착"}
                if name in negative_dims:
                    direction = "improved"
                    msg = f"{name}이 {abs(delta):.0f}점 낮아졌습니다. 좋은 변화예요!"
                else:
                    direction = "declined"
                    msg = f"{name}이 {abs(delta):.0f}점 낮아졌습니다."

            deltas.append(GrowthDelta(
                dimension=name, previous=prev, current=curr,
                delta=delta, direction=direction, message=msg,
            ))
        return deltas

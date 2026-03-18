"""사용자 심리 프로파일 모델"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .question import PsychDimension


class BigFiveProfile(BaseModel):
    """Big Five 성격 프로파일 (각 0~100)"""
    extraversion: float = 50.0       # 외향성
    neuroticism: float = 50.0        # 신경성
    conscientiousness: float = 50.0  # 성실성
    openness: float = 50.0           # 개방성
    agreeableness: float = 50.0      # 친화성


class AttachmentProfile(BaseModel):
    """애착 유형 프로파일"""
    secure: float = 0.0     # 안정형
    anxious: float = 0.0    # 불안형
    avoidant: float = 0.0   # 회피형

    @property
    def dominant_type(self) -> str:
        scores = {
            "안정형": self.secure,
            "불안형": self.anxious,
            "회피형": self.avoidant,
        }
        return max(scores, key=scores.get)


class LoveTriangleProfile(BaseModel):
    """Sternberg 사랑의 삼각이론 프로파일"""
    intimacy: float = 0.0    # 친밀감
    passion: float = 0.0     # 열정
    commitment: float = 0.0  # 헌신

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
            return "비사랑"


class UserProfile(BaseModel):
    """사용자 전체 심리 프로파일"""
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    big_five: BigFiveProfile = Field(default_factory=BigFiveProfile)
    attachment: AttachmentProfile = Field(default_factory=AttachmentProfile)
    love_triangle: LoveTriangleProfile = Field(default_factory=LoveTriangleProfile)
    answers: dict[str, int] = Field(default_factory=dict)  # question_id -> choice_index

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

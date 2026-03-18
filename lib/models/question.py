"""질문 모델 정의"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class QuestionCategory(str, Enum):
    """질문 카테고리 - Phase 1 여행 단계에 매핑"""
    EMOTION = "emotion"          # 감정 상태 체크
    VALUES = "values"            # 가치관
    BEHAVIOR = "behavior"        # 행동 패턴
    RELATIONSHIP = "relationship"  # 관계 스타일
    EXPERIENCE = "experience"    # 과거 경험


class PsychDimension(str, Enum):
    """심리학 측정 차원"""
    # Big Five
    EXTRAVERSION = "extraversion"        # 외향성
    NEUROTICISM = "neuroticism"          # 신경성
    CONSCIENTIOUSNESS = "conscientiousness"  # 성실성
    OPENNESS = "openness"                # 개방성
    AGREEABLENESS = "agreeableness"      # 친화성
    # Attachment
    ATTACHMENT_SECURE = "attachment_secure"    # 안정형
    ATTACHMENT_ANXIOUS = "attachment_anxious"  # 불안형
    ATTACHMENT_AVOIDANT = "attachment_avoidant"  # 회피형
    # Sternberg
    INTIMACY = "intimacy"      # 친밀감
    PASSION = "passion"        # 열정
    COMMITMENT = "commitment"  # 헌신


class Choice(BaseModel):
    """선택지"""
    text: str
    scores: dict[PsychDimension, float]  # 선택 시 부여되는 점수


class Question(BaseModel):
    """질문"""
    id: str
    category: QuestionCategory
    narrative: str          # 스토리 텍스트 ("당신은 숲 속에서...")
    question: str           # 실제 질문
    choices: list[Choice]
    dimensions: list[PsychDimension]  # 이 질문이 측정하는 차원들
    phase: int = 1          # 1: 자기이해, 2: 관계
    order: int = 0          # 표시 순서

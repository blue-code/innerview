"""결과 리포트 모델"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class InsightPriority(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TENSION = "tension"  # 모순/갈등 인사이트


class InsightItem(BaseModel):
    """하나의 인사이트"""
    title: str
    description: str
    empathy_message: str
    priority: InsightPriority = InsightPriority.SECONDARY
    color_hint: str = "purple"  # UI 색상 힌트 (purple, blue, pink, green, yellow)


class ActionStep(BaseModel):
    """구체적 행동 단계"""
    week: int  # 1, 2, 3, 4
    action: str
    reason: str


class ReportSection(BaseModel):
    """리포트 섹션"""
    title: str
    summary: str
    icon: str = ""  # UI 아이콘 힌트
    color: str = "purple"
    insights: list[InsightItem] = Field(default_factory=list)


class PersonalReport(BaseModel):
    """개인 심리 리포트 (Phase 1)"""
    profile_summary: str
    struggle_reason: str
    comfort_message: str
    sections: list[ReportSection] = Field(default_factory=list)
    action_tips: list[str] = Field(default_factory=list)
    action_plan: list[ActionStep] = Field(default_factory=list)
    tension_insights: list[InsightItem] = Field(default_factory=list)  # 모순/갈등
    growth_notes: list[str] = Field(default_factory=list)  # 성장 추적 메시지


class CoupleInsight(BaseModel):
    """커플 비교 인사이트 (Phase 2)"""
    area: str
    person_a_style: str
    person_b_style: str
    compatibility: str  # "strength", "conflict", "growth"
    advice: str
    priority: InsightPriority = InsightPriority.SECONDARY


class CoupleReport(BaseModel):
    """커플 분석 리포트 (Phase 2)"""
    couple_summary: str = ""  # "당신들은 ___한 커플입니다"
    strengths: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    insights: list[CoupleInsight] = Field(default_factory=list)
    conversation_guides: list[str] = Field(default_factory=list)
    profile_comparison: dict = Field(default_factory=dict)  # 두 사람 점수 비교 데이터

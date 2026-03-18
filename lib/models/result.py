"""결과 리포트 모델"""

from __future__ import annotations

from pydantic import BaseModel, Field


class InsightItem(BaseModel):
    """하나의 인사이트"""
    title: str           # "당신의 관계 패턴"
    description: str     # 상세 설명
    empathy_message: str  # 공감 메시지


class ReportSection(BaseModel):
    """리포트 섹션"""
    title: str
    summary: str
    insights: list[InsightItem] = Field(default_factory=list)


class PersonalReport(BaseModel):
    """개인 심리 리포트 (Phase 1)"""
    profile_summary: str     # "당신의 심리 프로파일"
    struggle_reason: str     # "당신이 힘든 이유"
    comfort_message: str     # "당신을 위로하는 메시지"
    sections: list[ReportSection] = Field(default_factory=list)
    action_tips: list[str] = Field(default_factory=list)


class CoupleInsight(BaseModel):
    """커플 비교 인사이트 (Phase 2)"""
    area: str               # "갈등 해결 스타일"
    person_a_style: str     # "대화를 원함"
    person_b_style: str     # "시간을 두고 싶어함"
    compatibility: str      # "충돌 가능 영역"
    advice: str             # "이 주제로 대화해보세요"


class CoupleReport(BaseModel):
    """커플 분석 리포트 (Phase 2)"""
    strengths: list[str] = Field(default_factory=list)    # 잘 맞는 영역
    conflicts: list[str] = Field(default_factory=list)    # 충돌 가능 영역
    improvements: list[str] = Field(default_factory=list)  # 개선 포인트
    insights: list[CoupleInsight] = Field(default_factory=list)
    conversation_guides: list[str] = Field(default_factory=list)  # 대화 가이드

"""커플 게임 모델 - Phase 2 게임성 요소"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class GameType(str, Enum):
    """커플 미니게임 타입"""
    PREDICT = "predict"          # 예측 게임: 상대가 어떤 답을 골랐을지 맞추기
    BALANCE = "balance"          # 밸런스 게임: 둘 다 같은 선택지 고르면 점수
    SECRET_CARD = "secret_card"  # 시크릿 카드: 상대에게만 보이는 비밀 메시지
    CHALLENGE = "challenge"      # 챌린지: 관계 개선 미션
    SYNC_CHECK = "sync_check"    # 싱크로율 체크: 얼마나 같은 생각?


class PredictQuestion(BaseModel):
    """예측 게임 질문 - 상대방의 답을 맞춰보세요"""
    id: str
    situation: str              # 상황 설명
    question: str               # "상대방은 어떤 선택을 할까요?"
    choices: list[str]
    category: str = "predict"


class BalanceQuestion(BaseModel):
    """밸런스 게임 질문 - 둘 다 같으면 싱크로 점수 UP"""
    id: str
    question: str               # "짜장면 vs 짬뽕" 같은 것
    option_a: str
    option_b: str
    weight: float = 1.0         # 싱크로 점수 가중치


class SecretCard(BaseModel):
    """시크릿 카드 - 상대에게만 전달되는 비밀 메시지"""
    id: str
    prompt: str                 # "상대에게 하고 싶지만 못했던 말은?"
    sender_id: str = ""
    message: str = ""           # 사용자가 작성
    revealed: bool = False


class ChallengeMission(BaseModel):
    """챌린지 미션 - 관계 개선 실천 과제"""
    id: str
    title: str
    description: str
    difficulty: int = 1         # 1~3
    reward_points: int = 10
    completed_by: list[str] = Field(default_factory=list)


class SyncResult(BaseModel):
    """싱크로율 결과"""
    total_questions: int
    matched: int
    sync_percentage: float
    highlights: list[str] = Field(default_factory=list)  # "음식 취향 100% 일치!"
    mismatches: list[str] = Field(default_factory=list)   # "여행 스타일은 정반대!"


class CoupleGameSession(BaseModel):
    """커플 게임 세션"""
    session_id: str
    player_a_id: str
    player_b_id: str
    current_round: int = 0
    total_rounds: int = 0
    score_a: int = 0            # 플레이어 A 포인트
    score_b: int = 0            # 플레이어 B 포인트
    sync_score: float = 0.0     # 싱크로율 (0~100)
    completed_games: list[GameType] = Field(default_factory=list)
    secret_cards: list[SecretCard] = Field(default_factory=list)
    challenges: list[ChallengeMission] = Field(default_factory=list)

    @property
    def couple_level(self) -> str:
        """총 점수 기반 커플 레벨"""
        total = self.score_a + self.score_b
        if total >= 200:
            return "소울메이트"
        elif total >= 150:
            return "텔레파시 커플"
        elif total >= 100:
            return "케미 폭발 커플"
        elif total >= 50:
            return "알아가는 중 커플"
        else:
            return "첫 만남 커플"

    @property
    def sync_grade(self) -> str:
        """싱크로율 등급"""
        if self.sync_score >= 90:
            return "S"
        elif self.sync_score >= 75:
            return "A"
        elif self.sync_score >= 60:
            return "B"
        elif self.sync_score >= 40:
            return "C"
        else:
            return "D"

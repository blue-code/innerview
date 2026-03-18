"""커플 게임 엔진 - 미니게임, 싱크로율, 챌린지 관리"""

from __future__ import annotations

import random
import uuid
from typing import Optional

from ..models.couple_game import (
    BalanceQuestion,
    ChallengeMission,
    CoupleGameSession,
    GameType,
    PredictQuestion,
    SecretCard,
    SyncResult,
)


# ──────────────────────────────────────────────
# 예측 게임 질문 세트
# ──────────────────────────────────────────────
PREDICT_QUESTIONS: list[dict] = [
    {
        "id": "PD01",
        "situation": "비 오는 일요일 아침, 아무 계획이 없습니다.",
        "question": "상대방은 뭘 하고 싶어할까요?",
        "choices": ["이불 속에서 넷플릭스", "비 맞으며 산책", "카페에서 책 읽기", "집에서 요리하기"],
    },
    {
        "id": "PD02",
        "situation": "둘이 여행을 갑니다. 숙소를 고르는 중입니다.",
        "question": "상대방이 선택할 숙소는?",
        "choices": ["감성 있는 한옥 스테이", "편리한 시티 호텔", "자연 속 글램핑", "게스트하우스 (새로운 사람 만남)"],
    },
    {
        "id": "PD03",
        "situation": "상대방이 스트레스를 많이 받은 날입니다.",
        "question": "상대방은 어떻게 풀까요?",
        "choices": ["혼자 조용히 있기", "나한테 전화해서 이야기하기", "운동하기", "맛있는 거 먹기"],
    },
    {
        "id": "PD04",
        "situation": "둘이 영화를 보기로 했습니다.",
        "question": "상대방이 고를 장르는?",
        "choices": ["로맨스", "액션/스릴러", "코미디", "다큐멘터리/드라마"],
    },
    {
        "id": "PD05",
        "situation": "상대방 생일에 서프라이즈를 준비하려 합니다.",
        "question": "상대방이 가장 좋아할 선물은?",
        "choices": ["직접 쓴 편지", "갖고 싶었던 물건", "함께하는 특별한 경험", "맛있는 음식"],
    },
    {
        "id": "PD06",
        "situation": "5년 후, 상대방은 어디에 있을까요?",
        "question": "상대방이 상상하는 5년 후 모습은?",
        "choices": ["커리어에서 크게 성장한 모습", "사랑하는 사람과 안정된 일상", "새로운 도시에서 새 출발", "지금과 비슷하지만 더 여유로운 삶"],
    },
    {
        "id": "PD07",
        "situation": "둘이 싸운 후 24시간이 지났습니다.",
        "question": "상대방은 어떻게 할까요?",
        "choices": ["먼저 연락한다", "연락을 기다린다", "아무 일 없었던 듯 행동한다", "편지나 메시지를 보낸다"],
    },
    {
        "id": "PD08",
        "situation": "함께 요리를 하기로 했습니다.",
        "question": "상대방의 역할은?",
        "choices": ["레시피 찾고 지휘하기", "재료 손질 묵묵히 하기", "맛보기 담당", "분위기 담당 (음악, 세팅)"],
    },
]

# ──────────────────────────────────────────────
# 밸런스 게임 질문 세트
# ──────────────────────────────────────────────
BALANCE_QUESTIONS: list[dict] = [
    {"id": "BL01", "question": "데이트 스타일", "option_a": "밖에서 활동적으로", "option_b": "집에서 편하게"},
    {"id": "BL02", "question": "갈등 해결법", "option_a": "바로 대화로 풀기", "option_b": "시간 두고 생각하기"},
    {"id": "BL03", "question": "사랑 표현", "option_a": "말로 표현 ('사랑해')", "option_b": "행동으로 표현 (챙김)"},
    {"id": "BL04", "question": "주말 아침", "option_a": "일찍 일어나서 활동", "option_b": "늦잠 + 브런치"},
    {"id": "BL05", "question": "여행 스타일", "option_a": "빡빡한 계획 여행", "option_b": "즉흥 자유 여행"},
    {"id": "BL06", "question": "SNS에 우리 사진", "option_a": "자주 올리고 싶다", "option_b": "안 올려도 괜찮다"},
    {"id": "BL07", "question": "이상적인 저녁", "option_a": "분위기 좋은 레스토랑", "option_b": "배달 시켜 소파에서"},
    {"id": "BL08", "question": "상대 친구 모임", "option_a": "같이 가고 싶다", "option_b": "각자 시간 보내기"},
    {"id": "BL09", "question": "고민이 있을 때", "option_a": "바로 상대에게 말한다", "option_b": "혼자 정리한 후 말한다"},
    {"id": "BL10", "question": "미래 계획", "option_a": "함께 세부적으로 계획", "option_b": "대충 방향만 맞추기"},
    {"id": "BL11", "question": "서프라이즈", "option_a": "좋아한다 (설렘!)", "option_b": "부담스럽다 (미리 말해줘)"},
    {"id": "BL12", "question": "연락 빈도", "option_a": "수시로 카톡 (일상 공유)", "option_b": "필요할 때만 연락"},
]

# ──────────────────────────────────────────────
# 시크릿 카드 프롬프트
# ──────────────────────────────────────────────
SECRET_CARD_PROMPTS: list[dict] = [
    {"id": "SC01", "prompt": "상대에게 한 번도 말하지 못한 고마운 점은?"},
    {"id": "SC02", "prompt": "상대와 함께한 순간 중 가장 행복했던 때는?"},
    {"id": "SC03", "prompt": "상대에게 미안했지만 말하지 못한 것이 있다면?"},
    {"id": "SC04", "prompt": "상대를 한 단어로 표현한다면?"},
    {"id": "SC05", "prompt": "상대에게 꼭 해주고 싶은 말은?"},
    {"id": "SC06", "prompt": "상대와 꼭 함께 해보고 싶은 것은?"},
]

# ──────────────────────────────────────────────
# 챌린지 미션
# ──────────────────────────────────────────────
CHALLENGE_MISSIONS: list[dict] = [
    {"id": "CH01", "title": "오늘의 고마움 전하기", "description": "오늘 상대에게 고마웠던 점 하나를 직접 말해주세요.", "difficulty": 1, "reward_points": 10},
    {"id": "CH02", "title": "3분 눈 맞춤", "description": "타이머를 맞추고 3분간 서로 눈을 바라보세요. 웃어도 괜찮아요.", "difficulty": 1, "reward_points": 15},
    {"id": "CH03", "title": "상대의 장점 5개 적기", "description": "종이에 상대의 장점 5개를 적어서 교환하세요.", "difficulty": 1, "reward_points": 10},
    {"id": "CH04", "title": "역할 바꾸기 데이트", "description": "평소 상대가 좋아하는 방식으로 데이트를 계획해보세요.", "difficulty": 2, "reward_points": 25},
    {"id": "CH05", "title": "감정 일기 공유", "description": "오늘 하루 느꼈던 감정을 3줄로 적어서 서로 공유하세요.", "difficulty": 2, "reward_points": 20},
    {"id": "CH06", "title": "서로의 스트레스 해소법 체험", "description": "상대가 스트레스를 풀 때 하는 것을 함께 해보세요.", "difficulty": 2, "reward_points": 20},
    {"id": "CH07", "title": "미래 버킷리스트 만들기", "description": "둘이 함께 하고 싶은 것 10개를 리스트로 만드세요.", "difficulty": 2, "reward_points": 25},
    {"id": "CH08", "title": "24시간 감사 릴레이", "description": "24시간 동안 번갈아가며 고마운 점을 메시지로 보내세요.", "difficulty": 3, "reward_points": 40},
    {"id": "CH09", "title": "과거의 나에게 편지 쓰기", "description": "연애 초기의 나에게 편지를 써서 상대에게 읽어주세요.", "difficulty": 3, "reward_points": 35},
    {"id": "CH10", "title": "디지털 디톡스 데이트", "description": "핸드폰 없이 3시간 데이트를 해보세요.", "difficulty": 3, "reward_points": 50},
]


class CoupleGameEngine:
    """커플 미니게임 엔진"""

    def create_session(self, player_a_id: str, player_b_id: str) -> CoupleGameSession:
        return CoupleGameSession(
            session_id=str(uuid.uuid4())[:8],
            player_a_id=player_a_id,
            player_b_id=player_b_id,
        )

    # ──── 예측 게임 ────

    def get_predict_questions(self, count: int = 5) -> list[PredictQuestion]:
        selected = random.sample(PREDICT_QUESTIONS, min(count, len(PREDICT_QUESTIONS)))
        return [PredictQuestion(**q) for q in selected]

    def score_predict(self, my_prediction: int, partner_actual: int) -> tuple[bool, int]:
        """예측이 맞았으면 (True, 점수), 틀렸으면 (False, 0)"""
        if my_prediction == partner_actual:
            return True, 15
        return False, 0

    # ──── 밸런스 게임 ────

    def get_balance_questions(self, count: int = 8) -> list[BalanceQuestion]:
        selected = random.sample(BALANCE_QUESTIONS, min(count, len(BALANCE_QUESTIONS)))
        return [BalanceQuestion(**q) for q in selected]

    def calculate_sync(
        self,
        answers_a: list[str],
        answers_b: list[str],
        questions: list[BalanceQuestion],
    ) -> SyncResult:
        """밸런스 게임 싱크로율 계산"""
        if len(answers_a) != len(answers_b):
            raise ValueError("답변 수가 일치하지 않습니다")

        matched = 0
        total = len(answers_a)
        highlights = []
        mismatches = []

        for i, (a, b) in enumerate(zip(answers_a, answers_b)):
            q = questions[i] if i < len(questions) else None
            q_text = q.question if q else f"질문 {i+1}"
            if a == b:
                matched += 1
                highlights.append(f"'{q_text}' 완벽 일치!")
            else:
                choice_a = q.option_a if a == "a" else q.option_b if q else a
                choice_b = q.option_a if b == "a" else q.option_b if q else b
                mismatches.append(f"'{q_text}': {choice_a} vs {choice_b}")

        sync_pct = (matched / total * 100) if total > 0 else 0

        return SyncResult(
            total_questions=total,
            matched=matched,
            sync_percentage=round(sync_pct, 1),
            highlights=highlights,
            mismatches=mismatches,
        )

    # ──── 시크릿 카드 ────

    def get_secret_card_prompts(self, count: int = 3) -> list[SecretCard]:
        selected = random.sample(SECRET_CARD_PROMPTS, min(count, len(SECRET_CARD_PROMPTS)))
        return [SecretCard(**p) for p in selected]

    def reveal_cards(self, cards: list[SecretCard]) -> list[SecretCard]:
        """카드를 공개 상태로 변경"""
        for card in cards:
            card.revealed = True
        return cards

    # ──── 챌린지 미션 ────

    def get_daily_challenge(self, difficulty: Optional[int] = None) -> ChallengeMission:
        pool = CHALLENGE_MISSIONS
        if difficulty:
            pool = [m for m in pool if m["difficulty"] == difficulty]
        if not pool:
            pool = CHALLENGE_MISSIONS
        return ChallengeMission(**random.choice(pool))

    def get_challenge_set(self, count: int = 3) -> list[ChallengeMission]:
        """난이도 균형 맞춘 챌린지 세트"""
        easy = [m for m in CHALLENGE_MISSIONS if m["difficulty"] == 1]
        medium = [m for m in CHALLENGE_MISSIONS if m["difficulty"] == 2]
        hard = [m for m in CHALLENGE_MISSIONS if m["difficulty"] == 3]

        result = []
        if easy:
            result.append(ChallengeMission(**random.choice(easy)))
        if medium:
            result.append(ChallengeMission(**random.choice(medium)))
        if hard:
            result.append(ChallengeMission(**random.choice(hard)))

        while len(result) < count and CHALLENGE_MISSIONS:
            result.append(ChallengeMission(**random.choice(CHALLENGE_MISSIONS)))
        return result[:count]

    def complete_challenge(
        self, session: CoupleGameSession, challenge_id: str, player_id: str
    ) -> int:
        """챌린지 완료 처리, 포인트 반환"""
        for ch in session.challenges:
            if ch.id == challenge_id and player_id not in ch.completed_by:
                ch.completed_by.append(player_id)
                if player_id == session.player_a_id:
                    session.score_a += ch.reward_points
                else:
                    session.score_b += ch.reward_points
                return ch.reward_points
        return 0

    # ──── 종합 게임 세션 ────

    def run_full_game(self, session: CoupleGameSession) -> CoupleGameSession:
        """전체 게임 세션 초기화"""
        session.total_rounds = 4  # predict + balance + secret + challenge
        session.challenges = self.get_challenge_set(3)
        session.secret_cards = self.get_secret_card_prompts(2)
        return session

    def generate_couple_title(self, session: CoupleGameSession) -> str:
        """커플 칭호 생성"""
        sync = session.sync_score
        level = session.couple_level

        titles = {
            "소울메이트": [
                "말하지 않아도 통하는 커플",
                "전생에 약속한 사이",
                "운명이 인정한 커플",
            ],
            "텔레파시 커플": [
                "눈빛만 봐도 아는 사이",
                "같은 생각 같은 마음",
                "케미 맛집 커플",
            ],
            "케미 폭발 커플": [
                "다르지만 끌리는 사이",
                "서로를 채워주는 커플",
                "반전 매력 커플",
            ],
            "알아가는 중 커플": [
                "설렘 가득한 탐험 중",
                "알수록 재미있는 사이",
                "가능성 무한 커플",
            ],
            "첫 만남 커플": [
                "새로운 시작의 설렘",
                "궁금한 게 많은 커플",
                "앞으로가 더 기대되는 사이",
            ],
        }

        options = titles.get(level, titles["알아가는 중 커플"])
        return random.choice(options)

"""커플 게임 엔진 테스트"""

import pytest
from lib.engines.couple_game_engine import CoupleGameEngine
from lib.models.couple_game import CoupleGameSession


class TestCoupleGameEngine:
    def setup_method(self):
        self.engine = CoupleGameEngine()

    def test_create_session(self):
        session = self.engine.create_session("alice", "bob")
        assert session.player_a_id == "alice"
        assert session.player_b_id == "bob"
        assert session.score_a == 0

    def test_get_predict_questions(self):
        qs = self.engine.get_predict_questions(3)
        assert len(qs) == 3
        assert all(q.question for q in qs)

    def test_score_predict_correct(self):
        correct, points = self.engine.score_predict(2, 2)
        assert correct is True
        assert points == 15

    def test_score_predict_wrong(self):
        correct, points = self.engine.score_predict(1, 3)
        assert correct is False
        assert points == 0

    def test_get_balance_questions(self):
        qs = self.engine.get_balance_questions(5)
        assert len(qs) == 5
        assert all(q.option_a and q.option_b for q in qs)

    def test_calculate_sync_perfect(self):
        qs = self.engine.get_balance_questions(4)
        answers = ["a", "b", "a", "b"]
        result = self.engine.calculate_sync(answers, answers, qs)
        assert result.sync_percentage == 100.0
        assert result.matched == 4
        assert len(result.mismatches) == 0

    def test_calculate_sync_none(self):
        qs = self.engine.get_balance_questions(4)
        a = ["a", "a", "a", "a"]
        b = ["b", "b", "b", "b"]
        result = self.engine.calculate_sync(a, b, qs)
        assert result.sync_percentage == 0.0
        assert result.matched == 0

    def test_calculate_sync_partial(self):
        qs = self.engine.get_balance_questions(4)
        a = ["a", "b", "a", "b"]
        b = ["a", "a", "b", "b"]
        result = self.engine.calculate_sync(a, b, qs)
        assert result.sync_percentage == 50.0
        assert result.matched == 2

    def test_secret_card_prompts(self):
        cards = self.engine.get_secret_card_prompts(3)
        assert len(cards) == 3
        assert all(c.prompt for c in cards)
        assert all(not c.revealed for c in cards)

    def test_reveal_cards(self):
        cards = self.engine.get_secret_card_prompts(2)
        revealed = self.engine.reveal_cards(cards)
        assert all(c.revealed for c in revealed)

    def test_daily_challenge(self):
        ch = self.engine.get_daily_challenge()
        assert ch.title
        assert ch.reward_points > 0

    def test_challenge_set_variety(self):
        challenges = self.engine.get_challenge_set(3)
        assert len(challenges) == 3
        difficulties = {c.difficulty for c in challenges}
        assert len(difficulties) >= 2

    def test_complete_challenge(self):
        session = self.engine.create_session("alice", "bob")
        session.challenges = self.engine.get_challenge_set(1)
        ch_id = session.challenges[0].id
        points = self.engine.complete_challenge(session, ch_id, "alice")
        assert points > 0
        assert session.score_a == points

    def test_complete_challenge_duplicate(self):
        session = self.engine.create_session("alice", "bob")
        session.challenges = self.engine.get_challenge_set(1)
        ch_id = session.challenges[0].id
        self.engine.complete_challenge(session, ch_id, "alice")
        points2 = self.engine.complete_challenge(session, ch_id, "alice")
        assert points2 == 0

    def test_couple_level(self):
        session = CoupleGameSession(
            session_id="test", player_a_id="a", player_b_id="b",
            score_a=100, score_b=110,
        )
        assert session.couple_level == "소울메이트"

    def test_sync_grade(self):
        session = CoupleGameSession(
            session_id="test", player_a_id="a", player_b_id="b",
            sync_score=92.0,
        )
        assert session.sync_grade == "S"

    def test_generate_couple_title(self):
        session = self.engine.create_session("a", "b")
        session.sync_score = 80
        title = self.engine.generate_couple_title(session)
        assert isinstance(title, str)
        assert len(title) > 0

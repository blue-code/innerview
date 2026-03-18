"""스코어링 엔진 테스트"""

import pytest
from lib.engines.scoring_engine import ScoringEngine


class TestScoringEngine:
    def test_initial_state(self):
        engine = ScoringEngine()
        assert engine.raw_scores == {}
        assert engine.answer_count == {}

    def test_add_scores(self):
        engine = ScoringEngine()
        engine.add_scores({"extraversion": 8, "openness": 7})
        assert engine.raw_scores["extraversion"] == 8
        assert engine.raw_scores["openness"] == 7
        assert engine.answer_count["extraversion"] == 1

    def test_add_scores_accumulate(self):
        engine = ScoringEngine()
        engine.add_scores({"extraversion": 8})
        engine.add_scores({"extraversion": 6})
        assert engine.raw_scores["extraversion"] == 14
        assert engine.answer_count["extraversion"] == 2

    def test_normalize(self):
        engine = ScoringEngine()
        engine.add_scores({"extraversion": 10})
        assert engine._normalize("extraversion") == 100.0

        engine2 = ScoringEngine()
        engine2.add_scores({"extraversion": 5})
        assert engine2._normalize("extraversion") == 50.0

    def test_normalize_default(self):
        engine = ScoringEngine()
        assert engine._normalize("nonexistent") == 50.0

    def test_build_big_five(self):
        engine = ScoringEngine()
        engine.add_scores({"extraversion": 8, "neuroticism": 3, "conscientiousness": 7})
        bf = engine.build_big_five()
        assert bf.extraversion == 80.0
        assert bf.neuroticism == 30.0
        assert bf.conscientiousness == 70.0
        assert bf.openness == 50.0  # default
        assert bf.agreeableness == 50.0  # default

    def test_build_attachment(self):
        engine = ScoringEngine()
        engine.add_scores({"attachment_secure": 8, "attachment_anxious": 3, "attachment_avoidant": 2})
        at = engine.build_attachment()
        assert at.secure == 80.0
        assert at.anxious == 30.0
        assert at.avoidant == 20.0
        assert at.dominant_type == "안정형"

    def test_build_love_triangle(self):
        engine = ScoringEngine()
        engine.add_scores({"intimacy": 9, "passion": 7, "commitment": 8})
        lt = engine.build_love_triangle()
        assert lt.intimacy == 90.0
        assert lt.passion == 70.0
        assert lt.commitment == 80.0
        assert lt.love_type == "완전한 사랑"

    def test_build_profile(self):
        engine = ScoringEngine()
        engine.add_scores({"extraversion": 8, "attachment_secure": 7, "intimacy": 9})
        profile = engine.build_profile("test-user")
        assert profile.user_id == "test-user"
        assert profile.big_five.extraversion == 80.0
        assert profile.attachment.secure == 70.0
        assert profile.love_triangle.intimacy == 90.0

    def test_reset(self):
        engine = ScoringEngine()
        engine.add_scores({"extraversion": 8})
        engine.reset()
        assert engine.raw_scores == {}
        assert engine.answer_count == {}

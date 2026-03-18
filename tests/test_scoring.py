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

    def test_normalize_with_weight(self):
        engine = ScoringEngine()
        engine.add_scores({"passion": 5})
        # weight 1.3 → 5 * 1.3 / 10 * 100 = 65
        assert engine._normalize("passion", weight=1.3) == 65.0

    def test_build_big_five(self):
        engine = ScoringEngine()
        engine.add_scores({"extraversion": 8, "neuroticism": 3, "conscientiousness": 7})
        bf = engine.build_big_five()
        assert bf.extraversion == 80.0
        assert bf.neuroticism == 30.0
        assert bf.conscientiousness == 70.0
        assert bf.openness == 50.0
        assert bf.agreeableness == 50.0

    def test_build_attachment(self):
        engine = ScoringEngine()
        engine.add_scores({"attachment_secure": 8, "attachment_anxious": 3, "attachment_avoidant": 2})
        at = engine.build_attachment()
        assert at.secure == 80.0
        assert at.anxious == 30.0
        assert at.avoidant == 20.0
        assert at.dominant_type == "안정형"

    def test_build_love_triangle_with_weights(self):
        engine = ScoringEngine()
        engine.add_scores({"intimacy": 5, "passion": 5, "commitment": 5})
        lt = engine.build_love_triangle()
        assert lt.intimacy == 50.0
        assert lt.passion == 65.0   # 5 * 1.3 = 6.5 → 65%
        assert lt.commitment == 70.0  # 5 * 1.4 = 7 → 70%

    def test_build_profile(self):
        engine = ScoringEngine()
        engine.add_scores({"extraversion": 8, "attachment_secure": 7, "intimacy": 9})
        profile = engine.build_profile("test-user")
        assert profile.user_id == "test-user"
        assert profile.big_five.extraversion == 80.0
        assert profile.attachment.secure == 70.0

    def test_get_confidence(self):
        engine = ScoringEngine()
        assert engine.get_confidence("extraversion") == "none"
        engine.add_scores({"extraversion": 5})
        assert engine.get_confidence("extraversion") == "low"
        engine.add_scores({"extraversion": 5})
        engine.add_scores({"extraversion": 5})
        assert engine.get_confidence("extraversion") == "medium"
        engine.add_scores({"extraversion": 5})
        engine.add_scores({"extraversion": 5})
        assert engine.get_confidence("extraversion") == "high"

    def test_get_all_confidences(self):
        engine = ScoringEngine()
        confs = engine.get_all_confidences()
        assert "extraversion" in confs
        assert confs["extraversion"] == "none"

    def test_reset(self):
        engine = ScoringEngine()
        engine.add_scores({"extraversion": 8})
        engine.reset()
        assert engine.raw_scores == {}
        assert engine.answer_count == {}

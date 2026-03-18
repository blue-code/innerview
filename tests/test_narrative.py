"""내러티브 엔진 테스트"""

import pytest
from lib.models.user_profile import UserProfile, BigFiveProfile, AttachmentProfile, LoveTriangleProfile
from lib.engines.narrative_engine import NarrativeEngine


class TestNarrativeEngine:
    def _make_profile(self, **kwargs) -> UserProfile:
        bf = kwargs.get("big_five", BigFiveProfile())
        at = kwargs.get("attachment", AttachmentProfile())
        lt = kwargs.get("love_triangle", LoveTriangleProfile())
        return UserProfile(
            user_id="test",
            big_five=bf,
            attachment=at,
            love_triangle=lt,
        )

    def test_generate_report_has_all_fields(self):
        engine = NarrativeEngine()
        profile = self._make_profile()
        report = engine.generate_report(profile)
        assert report.profile_summary
        assert report.struggle_reason
        assert report.comfort_message
        assert len(report.sections) == 3
        assert len(report.action_tips) > 0

    def test_high_neuroticism_report(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            big_five=BigFiveProfile(neuroticism=80),
        )
        report = engine.generate_report(profile)
        assert "감정" in report.struggle_reason or "힘든" in report.struggle_reason

    def test_anxious_attachment_comfort(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            attachment=AttachmentProfile(secure=20, anxious=80, avoidant=10),
        )
        report = engine.generate_report(profile)
        assert "사랑" in report.comfort_message

    def test_avoidant_attachment_comfort(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            attachment=AttachmentProfile(secure=20, anxious=10, avoidant=80),
        )
        report = engine.generate_report(profile)
        assert "혼자" in report.comfort_message or "기대" in report.comfort_message

    def test_complete_love_type(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            love_triangle=LoveTriangleProfile(intimacy=80, passion=80, commitment=80),
        )
        report = engine.generate_report(profile)
        love_section = report.sections[2]
        assert "완전한 사랑" in love_section.summary

    def test_personality_section_extraverted(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            big_five=BigFiveProfile(extraversion=80),
        )
        report = engine.generate_report(profile)
        personality = report.sections[0]
        assert any("활력" in i.description or "사람" in i.description for i in personality.insights)

    def test_personality_section_introverted(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            big_five=BigFiveProfile(extraversion=20),
        )
        report = engine.generate_report(profile)
        personality = report.sections[0]
        assert any("내면" in i.title for i in personality.insights)

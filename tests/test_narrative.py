"""내러티브 엔진 테스트"""

import pytest
from lib.models.user_profile import UserProfile, BigFiveProfile, AttachmentProfile, LoveTriangleProfile
from lib.engines.narrative_engine import NarrativeEngine


class TestNarrativeEngine:
    def _make_profile(self, **kwargs) -> UserProfile:
        bf = kwargs.get("big_five", BigFiveProfile())
        at = kwargs.get("attachment", AttachmentProfile())
        lt = kwargs.get("love_triangle", LoveTriangleProfile())
        return UserProfile(user_id="test", big_five=bf, attachment=at, love_triangle=lt)

    def test_generate_report_has_all_fields(self):
        engine = NarrativeEngine()
        profile = self._make_profile()
        report = engine.generate_report(profile)
        assert report.profile_summary
        assert report.struggle_reason
        assert report.comfort_message
        assert len(report.sections) == 3
        assert len(report.action_tips) > 0
        assert len(report.action_plan) == 4  # 4주 플랜

    def test_high_neuroticism_report(self):
        engine = NarrativeEngine()
        profile = self._make_profile(big_five=BigFiveProfile(neuroticism=80))
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

    def test_mixed_attachment_comfort(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            attachment=AttachmentProfile(secure=30, anxious=70, avoidant=65),
        )
        report = engine.generate_report(profile)
        assert "공존" in report.comfort_message or "상반" in report.comfort_message

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
        profile = self._make_profile(big_five=BigFiveProfile(extraversion=80))
        report = engine.generate_report(profile)
        personality = report.sections[0]
        assert any("활력" in i.description or "사람" in i.description for i in personality.insights)

    def test_personality_section_introverted(self):
        engine = NarrativeEngine()
        profile = self._make_profile(big_five=BigFiveProfile(extraversion=20))
        report = engine.generate_report(profile)
        personality = report.sections[0]
        assert any("내면" in i.title for i in personality.insights)

    def test_multi_variable_extrovert_neurotic(self):
        engine = NarrativeEngine()
        profile = self._make_profile(big_five=BigFiveProfile(extraversion=75, neuroticism=75))
        report = engine.generate_report(profile)
        personality = report.sections[0]
        assert any("불안" in i.title or "활발" in i.title for i in personality.insights)

    def test_multi_variable_introvert_agreeable(self):
        engine = NarrativeEngine()
        profile = self._make_profile(big_five=BigFiveProfile(extraversion=30, agreeableness=75))
        report = engine.generate_report(profile)
        personality = report.sections[0]
        assert any("맞춰" in i.title or "조용" in i.title for i in personality.insights)

    def test_tension_insights_generated(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            big_five=BigFiveProfile(agreeableness=75),
            attachment=AttachmentProfile(secure=30, anxious=70, avoidant=30),
        )
        report = engine.generate_report(profile)
        assert len(report.tension_insights) > 0

    def test_attachment_spectrum_mixed(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            attachment=AttachmentProfile(secure=30, anxious=70, avoidant=65),
        )
        report = engine.generate_report(profile)
        at_section = report.sections[1]
        assert any("복합" in i.title or "갈등" in i.title for i in at_section.insights)

    def test_attachment_bigfive_interaction(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            big_five=BigFiveProfile(conscientiousness=75),
            attachment=AttachmentProfile(secure=30, anxious=30, avoidant=70),
        )
        report = engine.generate_report(profile)
        at_section = report.sections[1]
        assert any("일" in i.title or "독립" in i.title for i in at_section.insights)

    def test_action_plan_4_weeks(self):
        engine = NarrativeEngine()
        profile = self._make_profile()
        report = engine.generate_report(profile)
        assert len(report.action_plan) == 4
        weeks = [s.week for s in report.action_plan]
        assert weeks == [1, 2, 3, 4]

    def test_tips_aligned_with_profile(self):
        """회피형에게 감정 일기 대신 작은 표현 추천"""
        engine = NarrativeEngine()
        profile = self._make_profile(
            big_five=BigFiveProfile(neuroticism=70, extraversion=30),
            attachment=AttachmentProfile(secure=20, anxious=20, avoidant=75),
        )
        report = engine.generate_report(profile)
        # 회피형이므로 '감정 일기'가 아닌 다른 팁
        tip_texts = " ".join(report.action_tips)
        assert "작은" in tip_texts or "표현" in tip_texts or "적어" in tip_texts

    def test_growth_notes_with_previous(self):
        engine = NarrativeEngine()
        previous = self._make_profile(big_five=BigFiveProfile(neuroticism=80))
        current = self._make_profile(big_five=BigFiveProfile(neuroticism=60))
        report = engine.generate_report(current, previous)
        assert len(report.growth_notes) > 0

    def test_love_section_has_strongest_weakest(self):
        engine = NarrativeEngine()
        profile = self._make_profile(
            love_triangle=LoveTriangleProfile(intimacy=80, passion=40, commitment=60),
        )
        report = engine.generate_report(profile)
        love_section = report.sections[2]
        assert any("강한" in i.title for i in love_section.insights)

    def test_section_colors(self):
        engine = NarrativeEngine()
        profile = self._make_profile()
        report = engine.generate_report(profile)
        assert report.sections[0].color == "blue"
        assert report.sections[1].color == "pink"
        assert report.sections[2].color == "pink"

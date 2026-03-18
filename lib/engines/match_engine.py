"""매칭 엔진 - 두 사람의 프로파일 비교 (Phase 2)"""

from __future__ import annotations

from ..models.user_profile import UserProfile
from ..models.result import CoupleReport, CoupleInsight


class MatchEngine:
    """두 사용자의 심리 프로파일을 비교하여 커플 리포트 생성"""

    def compare(self, profile_a: UserProfile, profile_b: UserProfile) -> CoupleReport:
        strengths = []
        conflicts = []
        improvements = []
        insights = []
        guides = []

        # Big Five 비교
        bf_a, bf_b = profile_a.big_five, profile_b.big_five

        # 외향성 차이
        ext_diff = abs(bf_a.extraversion - bf_b.extraversion)
        if ext_diff < 20:
            strengths.append("사회적 활동에 대한 선호가 비슷합니다")
        elif ext_diff > 40:
            conflicts.append("사교 활동에 대한 선호 차이가 큽니다")
            insights.append(CoupleInsight(
                area="사교 활동",
                person_a_style=self._ext_label(bf_a.extraversion),
                person_b_style=self._ext_label(bf_b.extraversion),
                compatibility="충돌 가능 영역",
                advice="주말 계획을 세울 때, 서로의 에너지 충전 방식을 존중해보세요.",
            ))
            guides.append("'이번 주말에 어떻게 쉬고 싶어?'라고 물어보세요")

        # 신경성 비교
        neu_diff = abs(bf_a.neuroticism - bf_b.neuroticism)
        if neu_diff > 40:
            conflicts.append("감정 표현과 반응 방식에 차이가 있습니다")
            high_neu = "A" if bf_a.neuroticism > bf_b.neuroticism else "B"
            insights.append(CoupleInsight(
                area="감정 표현",
                person_a_style="감정에 민감한 편" if bf_a.neuroticism > 60 else "감정적으로 안정적",
                person_b_style="감정에 민감한 편" if bf_b.neuroticism > 60 else "감정적으로 안정적",
                compatibility="주의 필요 영역",
                advice=f"감정이 큰 쪽의 표현을 평가하지 말고, 먼저 들어주세요.",
            ))

        # 친화성 비교
        agr_avg = (bf_a.agreeableness + bf_b.agreeableness) / 2
        if agr_avg > 65:
            strengths.append("서로에 대한 배려심이 높은 커플입니다")
        elif agr_avg < 35:
            improvements.append("서로의 입장을 이해하려는 노력이 필요합니다")
            guides.append("'네 입장에서는 어떻게 느꼈어?'라고 물어보세요")

        # 애착 유형 비교
        at_a, at_b = profile_a.attachment, profile_b.attachment
        type_a, type_b = at_a.dominant_type, at_b.dominant_type

        attachment_insight = self._attachment_compatibility(type_a, type_b)
        insights.append(attachment_insight)

        if type_a == "안정형" and type_b == "안정형":
            strengths.append("두 사람 모두 안정적인 관계 패턴을 가지고 있습니다")
        elif "불안형" in (type_a, type_b) and "회피형" in (type_a, type_b):
            conflicts.append("불안-회피 패턴이 나타날 수 있습니다")
            guides.append("갈등 시 '지금 나는 불안해서 이렇게 행동하는 거야'라고 솔직하게 말해보세요")
            improvements.append("서로의 애착 패턴을 이해하고, 반응이 아닌 의도를 봐주세요")

        # 사랑의 삼각이론 비교
        lt_a, lt_b = profile_a.love_triangle, profile_b.love_triangle

        int_diff = abs(lt_a.intimacy - lt_b.intimacy)
        pas_diff = abs(lt_a.passion - lt_b.passion)
        com_diff = abs(lt_a.commitment - lt_b.commitment)

        if int_diff < 20 and pas_diff < 20 and com_diff < 20:
            strengths.append("사랑에 대한 가치관이 비슷합니다")
        else:
            if pas_diff > 30:
                improvements.append("서로가 원하는 관계의 '온도'가 다를 수 있습니다")
                guides.append("'우리 관계에서 어떤 부분이 가장 중요해?'라고 대화해보세요")

        if not strengths:
            strengths.append("서로 다르기 때문에 배울 수 있는 점이 많은 관계입니다")
        if not guides:
            guides.append("일주일에 한 번, 서로의 감정을 공유하는 시간을 가져보세요")

        return CoupleReport(
            strengths=strengths,
            conflicts=conflicts,
            improvements=improvements,
            insights=insights,
            conversation_guides=guides,
        )

    def _ext_label(self, score: float) -> str:
        if score > 65:
            return "활발한 사교 활동을 즐기는 편"
        elif score < 35:
            return "조용하고 소수의 관계를 선호하는 편"
        return "상황에 따라 유연한 편"

    def _attachment_compatibility(self, type_a: str, type_b: str) -> CoupleInsight:
        combos = {
            ("안정형", "안정형"): CoupleInsight(
                area="관계 안정성",
                person_a_style="안정형",
                person_b_style="안정형",
                compatibility="잘 맞는 영역",
                advice="서로의 안정감을 잘 유지하고 있습니다. 가끔 새로운 경험을 함께 시도해보세요.",
            ),
            ("불안형", "회피형"): CoupleInsight(
                area="관계 패턴",
                person_a_style="불안형 — 가까이 가고 싶어함",
                person_b_style="회피형 — 거리를 두고 싶어함",
                compatibility="충돌 가능 영역",
                advice="서로의 반응을 '거부'가 아닌 '보호 방식'으로 이해해보세요. 불안한 쪽은 잠시 기다려주고, 회피하는 쪽은 작은 표현이라도 해주세요.",
            ),
            ("회피형", "불안형"): CoupleInsight(
                area="관계 패턴",
                person_a_style="회피형 — 거리를 두고 싶어함",
                person_b_style="불안형 — 가까이 가고 싶어함",
                compatibility="충돌 가능 영역",
                advice="서로의 반응을 '거부'가 아닌 '보호 방식'으로 이해해보세요.",
            ),
        }

        key = (type_a, type_b)
        if key in combos:
            return combos[key]

        return CoupleInsight(
            area="관계 패턴",
            person_a_style=type_a,
            person_b_style=type_b,
            compatibility="이해가 필요한 영역",
            advice="서로의 관계 스타일을 이해하고, 다름을 인정하는 것이 첫걸음입니다.",
        )

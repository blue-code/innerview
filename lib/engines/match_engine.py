"""매칭 엔진 - 다차원 커플 프로파일 비교 (Phase 2)"""

from __future__ import annotations

from ..models.user_profile import UserProfile
from ..models.result import CoupleReport, CoupleInsight, InsightPriority


class MatchEngine:
    """두 사용자의 심리 프로파일을 비교하여 커플 리포트 생성"""

    def compare(self, profile_a: UserProfile, profile_b: UserProfile) -> CoupleReport:
        strengths = []
        conflicts = []
        improvements = []
        insights = []
        guides = []

        bf_a, bf_b = profile_a.big_five, profile_b.big_five
        at_a, at_b = profile_a.attachment, profile_b.attachment
        lt_a, lt_b = profile_a.love_triangle, profile_b.love_triangle

        # ──── Big Five 비교 ────

        # 외향성
        ext_diff = abs(bf_a.extraversion - bf_b.extraversion)
        if ext_diff < 20:
            strengths.append("사회적 활동에 대한 선호가 비슷합니다")
        elif ext_diff > 40:
            conflicts.append("사교 활동에 대한 선호 차이가 큽니다")
            insights.append(CoupleInsight(
                area="사교 활동",
                person_a_style=self._ext_label(bf_a.extraversion),
                person_b_style=self._ext_label(bf_b.extraversion),
                compatibility="conflict",
                advice="주말 계획을 세울 때, 서로의 에너지 충전 방식을 존중해보세요. 활동과 휴식의 균형을 함께 찾아보세요.",
                priority=InsightPriority.PRIMARY,
            ))
            guides.append("'이번 주말에 어떻게 쉬고 싶어?'라고 물어보세요")
        else:
            # 중간 차이: 보완적
            strengths.append("사교 활동 선호가 적당히 달라서 서로 새로운 경험을 줄 수 있습니다")

        # 신경성
        neu_diff = abs(bf_a.neuroticism - bf_b.neuroticism)
        if neu_diff > 40:
            conflicts.append("감정 표현과 반응 방식에 차이가 있습니다")
            insights.append(CoupleInsight(
                area="감정 표현",
                person_a_style="감정에 민감한 편" if bf_a.neuroticism > 60 else "감정적으로 안정적",
                person_b_style="감정에 민감한 편" if bf_b.neuroticism > 60 else "감정적으로 안정적",
                compatibility="conflict",
                advice="감정이 큰 쪽의 표현을 '예민하다'고 평가하지 말고, 먼저 들어주세요. 안정적인 쪽은 안전한 닻 역할을 해줄 수 있어요.",
            ))
        elif neu_diff < 15:
            strengths.append("감정의 온도가 비슷해서 서로를 이해하기 쉽습니다")

        # 성실성
        con_diff = abs(bf_a.conscientiousness - bf_b.conscientiousness)
        if con_diff > 35:
            conflicts.append("계획과 즉흥에 대한 선호가 다릅니다")
            insights.append(CoupleInsight(
                area="생활 스타일",
                person_a_style="계획적인 편" if bf_a.conscientiousness > 60 else "즉흥적인 편",
                person_b_style="계획적인 편" if bf_b.conscientiousness > 60 else "즉흥적인 편",
                compatibility="growth",
                advice="계획적인 쪽은 때로는 상대의 즉흥성에서 자유를 배울 수 있고, 즉흥적인 쪽은 상대의 계획성에서 안정을 배울 수 있어요.",
            ))
            guides.append("여행 계획을 세울 때 '반은 계획, 반은 즉흥'으로 해보세요")

        # 친화성
        agr_a, agr_b = bf_a.agreeableness, bf_b.agreeableness
        agr_avg = (agr_a + agr_b) / 2
        if agr_avg > 65:
            strengths.append("서로에 대한 배려심이 높은 커플입니다")
        elif agr_avg < 35:
            improvements.append("서로의 입장을 이해하려는 노력이 필요합니다")
            guides.append("'네 입장에서는 어떻게 느꼈어?'라고 물어보세요")
        # 한쪽만 높은 경우
        if abs(agr_a - agr_b) > 30:
            high_name = "A" if agr_a > agr_b else "B"
            improvements.append(f"배려의 균형이 한쪽으로 기울 수 있습니다. 받는 쪽도 표현해주세요.")

        # 개방성
        opn_diff = abs(bf_a.openness - bf_b.openness)
        if opn_diff < 20:
            strengths.append("새로운 경험에 대한 태도가 비슷합니다")
        elif opn_diff > 35:
            insights.append(CoupleInsight(
                area="새로운 경험",
                person_a_style="도전적인 편" if bf_a.openness > 60 else "익숙한 것을 선호",
                person_b_style="도전적인 편" if bf_b.openness > 60 else "익숙한 것을 선호",
                compatibility="growth",
                advice="한쪽이 새로운 것을 제안할 때, 바로 거절하기보다 '한 번 해볼까?'라고 열어두세요.",
            ))

        # ──── 애착 유형 비교 (스펙트럼 기반) ────

        type_a, type_b = at_a.dominant_type, at_b.dominant_type
        insights.append(self._attachment_compatibility(at_a, at_b))

        if type_a == "안정형" and type_b == "안정형":
            strengths.append("두 사람 모두 안정적인 관계 패턴을 가지고 있습니다")
        elif type_a == "안정형" or type_b == "안정형":
            strengths.append("한 사람의 안정형 패턴이 관계에 안전 기반이 됩니다")
            guides.append("안정형인 쪽이 상대의 불안이나 거리두기를 '나에 대한 것'으로 받아들이지 마세요")
        elif ("불안형" in (type_a, type_b)) and ("회피형" in (type_a, type_b)):
            conflicts.append("불안-회피 추격 패턴이 나타날 수 있습니다")
            guides.append("갈등 시 '지금 나는 불안해서 이렇게 행동하는 거야'라고 솔직하게 말해보세요")
            improvements.append("서로의 애착 패턴을 '거부'가 아닌 '보호 방식'으로 이해해주세요")

        # ──── 사랑의 삼각이론 비교 ────

        int_diff = abs(lt_a.intimacy - lt_b.intimacy)
        pas_diff = abs(lt_a.passion - lt_b.passion)
        com_diff = abs(lt_a.commitment - lt_b.commitment)

        if int_diff < 15 and pas_diff < 15 and com_diff < 15:
            strengths.append("사랑에 대한 가치관이 매우 비슷합니다")
        else:
            love_insights = self._love_comparison(lt_a, lt_b)
            insights.extend(love_insights)
            if pas_diff > 30:
                improvements.append("서로가 원하는 관계의 '온도'가 다를 수 있습니다")
                guides.append("'우리 관계에서 어떤 부분이 가장 중요해?'라고 대화해보세요")
            if com_diff > 30:
                guides.append("미래에 대한 생각을 부담 없이 나눠보세요. 서로의 속도가 다를 수 있어요.")

        if not strengths:
            strengths.append("서로 다르기 때문에 배울 수 있는 점이 많은 관계입니다")
        if not guides:
            guides.append("일주일에 한 번, 서로의 감정을 공유하는 시간을 가져보세요")

        # 프로파일 비교 데이터 생성
        comparison = self._build_comparison_data(profile_a, profile_b)

        # 커플 종합 요약
        couple_summary = self._generate_couple_summary(
            strengths, conflicts, type_a, type_b, lt_a, lt_b
        )

        return CoupleReport(
            couple_summary=couple_summary,
            strengths=strengths,
            conflicts=conflicts,
            improvements=improvements,
            insights=insights,
            conversation_guides=guides,
            profile_comparison=comparison,
        )

    def _ext_label(self, score: float) -> str:
        if score > 65:
            return "활발한 사교 활동을 즐기는 편"
        elif score < 35:
            return "조용하고 소수의 관계를 선호하는 편"
        return "상황에 따라 유연한 편"

    def _attachment_compatibility(self, at_a, at_b) -> CoupleInsight:
        type_a, type_b = at_a.dominant_type, at_b.dominant_type

        if type_a == "안정형" and type_b == "안정형":
            return CoupleInsight(
                area="관계 안정성", person_a_style="안정형", person_b_style="안정형",
                compatibility="strength",
                advice="서로의 안정감을 잘 유지하고 있습니다. 가끔 새로운 경험을 함께 시도해보세요.",
                priority=InsightPriority.PRIMARY,
            )

        if ("불안형" in (type_a, type_b)) and ("회피형" in (type_a, type_b)):
            anxious_side = "A" if type_a == "불안형" else "B"
            return CoupleInsight(
                area="관계 패턴: 추격-도주 사이클",
                person_a_style=f"{type_a} — {'가까이 가고 싶어함' if type_a == '불안형' else '거리를 두고 싶어함'}",
                person_b_style=f"{type_b} — {'가까이 가고 싶어함' if type_b == '불안형' else '거리를 두고 싶어함'}",
                compatibility="conflict",
                advice="불안한 쪽이 다가갈수록 회피하는 쪽은 더 멀어집니다. "
                       "이 패턴을 인식하는 것이 첫걸음이에요. "
                       "불안한 쪽은 잠시 기다려주고, 회피하는 쪽은 작은 표현이라도 해주세요.",
                priority=InsightPriority.PRIMARY,
            )

        # 같은 유형
        if type_a == type_b:
            if type_a == "불안형":
                return CoupleInsight(
                    area="관계 패턴", person_a_style="불안형", person_b_style="불안형",
                    compatibility="growth",
                    advice="둘 다 사랑에 대한 확인이 필요한 편이에요. 서로에게 '사랑해'를 자주 표현하면 불안이 줄어들 수 있어요.",
                    priority=InsightPriority.PRIMARY,
                )
            if type_a == "회피형":
                return CoupleInsight(
                    area="관계 패턴", person_a_style="회피형", person_b_style="회피형",
                    compatibility="growth",
                    advice="둘 다 거리를 두는 경향이 있어서, 관계가 겉돌 수 있어요. 일주일에 한 번 감정 공유 시간을 정해보세요.",
                    priority=InsightPriority.PRIMARY,
                )

        return CoupleInsight(
            area="관계 패턴", person_a_style=type_a, person_b_style=type_b,
            compatibility="growth",
            advice="서로의 관계 스타일을 이해하고, 다름을 인정하는 것이 첫걸음입니다.",
        )

    def _love_comparison(self, lt_a, lt_b) -> list[CoupleInsight]:
        """사랑의 삼각이론 세부 비교"""
        insights = []

        dims = [
            ("친밀감", lt_a.intimacy, lt_b.intimacy),
            ("열정", lt_a.passion, lt_b.passion),
            ("헌신", lt_a.commitment, lt_b.commitment),
        ]

        for name, va, vb in dims:
            diff = abs(va - vb)
            if diff > 25:
                high_who = "A" if va > vb else "B"
                insights.append(CoupleInsight(
                    area=f"사랑의 요소: {name}",
                    person_a_style=f"{name} {'높음' if va > 60 else '보통' if va > 40 else '낮음'} ({va:.0f})",
                    person_b_style=f"{name} {'높음' if vb > 60 else '보통' if vb > 40 else '낮음'} ({vb:.0f})",
                    compatibility="growth",
                    advice=self._love_dim_advice(name, va, vb),
                ))

        return insights

    def _love_dim_advice(self, dim: str, va: float, vb: float) -> str:
        advices = {
            "친밀감": "깊은 대화의 시간을 더 자주 가져보세요. 서로의 내면을 알아가는 것이 친밀감을 높여줍니다.",
            "열정": "일상에 작은 변화를 주세요. 새로운 데이트, 깜짝 이벤트가 설렘을 되살려줍니다.",
            "헌신": "미래에 대한 생각을 솔직하게 나눠보세요. 서로의 속도가 다를 수 있으니 이해하는 것이 중요해요.",
        }
        return advices.get(dim, "서로의 차이를 대화로 풀어보세요.")

    def _build_comparison_data(self, pa: UserProfile, pb: UserProfile) -> dict:
        """UI에서 사용할 비교 데이터"""
        return {
            "big_five": {
                "a": pa.big_five.model_dump(),
                "b": pb.big_five.model_dump(),
            },
            "attachment": {
                "a": {"secure": pa.attachment.secure, "anxious": pa.attachment.anxious, "avoidant": pa.attachment.avoidant,
                      "dominant": pa.attachment.dominant_type, "blend": pa.attachment.blend_description},
                "b": {"secure": pb.attachment.secure, "anxious": pb.attachment.anxious, "avoidant": pb.attachment.avoidant,
                      "dominant": pb.attachment.dominant_type, "blend": pb.attachment.blend_description},
            },
            "love_triangle": {
                "a": {"intimacy": pa.love_triangle.intimacy, "passion": pa.love_triangle.passion,
                      "commitment": pa.love_triangle.commitment, "type": pa.love_triangle.love_type},
                "b": {"intimacy": pb.love_triangle.intimacy, "passion": pb.love_triangle.passion,
                      "commitment": pb.love_triangle.commitment, "type": pb.love_triangle.love_type},
            },
        }

    def _generate_couple_summary(self, strengths, conflicts, type_a, type_b, lt_a, lt_b) -> str:
        """커플 종합 요약 한 문장"""
        s_count = len(strengths)
        c_count = len(conflicts)

        if s_count > c_count + 2:
            tone = "서로를 잘 이해하고 있는"
        elif c_count > s_count + 1:
            tone = "서로를 더 알아가야 하는"
        else:
            tone = "다름 속에서 배우는"

        love_a, love_b = lt_a.love_type, lt_b.love_type
        if love_a == love_b:
            love_desc = f"같은 사랑의 언어({love_a})를 가진"
        else:
            love_desc = f"서로 다른 사랑의 언어를 가진"

        return f"당신들은 {tone}, {love_desc} 커플입니다."

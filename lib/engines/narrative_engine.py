"""내러티브 엔진 - 다변수 조합 기반 공감형 결과 생성"""

from __future__ import annotations

from typing import Optional

from ..models.user_profile import UserProfile, GrowthDelta
from ..models.result import (
    PersonalReport, ReportSection, InsightItem, InsightPriority,
    ActionStep,
)


class NarrativeEngine:
    """심리 프로파일을 기반으로 공감형 결과 리포트를 생성"""

    def generate_report(self, profile: UserProfile, previous: Optional[UserProfile] = None) -> PersonalReport:
        bf = profile.big_five
        at = profile.attachment
        lt = profile.love_triangle

        sections = [
            self._personality_section(bf),
            self._attachment_section(at, bf),
            self._love_section(lt),
        ]

        tension_insights = self._generate_tensions(bf, at, lt)
        growth_notes = []
        if previous:
            deltas = profile.compare_with(previous)
            growth_notes = [d.message for d in deltas if d.direction != "stable"]

        return PersonalReport(
            profile_summary=self._generate_summary(bf, at),
            struggle_reason=self._generate_struggle(bf, at),
            comfort_message=self._generate_comfort(bf, at),
            sections=sections,
            action_tips=self._generate_tips(bf, at, lt),
            action_plan=self._generate_action_plan(bf, at, lt),
            tension_insights=tension_insights,
            growth_notes=growth_notes,
        )

    # ──── 성격 섹션 ────

    def _personality_section(self, bf) -> ReportSection:
        insights = []

        # 다변수 조합 인사이트 (우선순위: PRIMARY)
        combo_insights = self._multi_variable_personality(bf)
        insights.extend(combo_insights)

        # 단일 차원 인사이트 (우선순위: SECONDARY)
        if bf.extraversion > 65:
            insights.append(InsightItem(
                title="사람과의 연결에서 에너지를 얻는 사람",
                description="당신은 사람들과 함께할 때 활력을 느끼고, 새로운 만남에서 즐거움을 찾습니다.",
                empathy_message="그래서 혼자 있는 시간이 길어지면 조금 답답하게 느껴질 수 있어요.",
                color_hint="pink",
            ))
        elif bf.extraversion < 35:
            insights.append(InsightItem(
                title="내면의 세계가 풍부한 사람",
                description="당신은 혼자만의 시간에서 에너지를 충전하고, 깊은 생각과 내면의 대화를 즐깁니다.",
                empathy_message="사교적이지 않다고 해서 사람을 싫어하는 게 아니에요. 당신만의 방식으로 세상과 연결되는 것뿐이에요.",
                color_hint="blue",
            ))

        if bf.neuroticism > 65:
            insights.append(InsightItem(
                title="감정이 섬세한 사람",
                description="당신은 감정의 변화를 크게 느끼고, 작은 것에도 깊이 반응합니다.",
                empathy_message="그게 때로는 힘들 수 있지만, 그만큼 세상을 깊이 느낄 수 있는 능력이기도 해요.",
                color_hint="yellow",
            ))
        elif bf.neuroticism < 35:
            insights.append(InsightItem(
                title="감정적으로 안정된 사람",
                description="당신은 스트레스 상황에서도 비교적 평온함을 유지할 수 있습니다.",
                empathy_message="때로는 감정을 너무 억누르고 있진 않은지 스스로에게 물어보는 것도 좋아요.",
                color_hint="green",
            ))

        if bf.openness > 65:
            insights.append(InsightItem(
                title="새로운 경험에 열린 사람",
                description="당신은 호기심이 많고, 익숙하지 않은 것에도 도전하는 것을 즐깁니다.",
                empathy_message="늘 새로운 것을 찾아 떠나는 당신, 때로는 지금 있는 곳에서 머무는 것도 괜찮아요.",
                color_hint="blue",
            ))

        if bf.conscientiousness > 65:
            insights.append(InsightItem(
                title="계획적이고 책임감 있는 사람",
                description="당신은 목표를 세우고 꾸준히 노력하는 것을 중요하게 여깁니다.",
                empathy_message="항상 완벽해야 한다는 압박을 느끼고 있지는 않나요? 가끔은 계획 없이 흘러가는 것도 좋아요.",
                color_hint="green",
            ))

        if bf.agreeableness > 65:
            insights.append(InsightItem(
                title="타인을 먼저 생각하는 따뜻한 사람",
                description="당신은 다른 사람의 감정에 공감하고, 조화를 중요하게 여깁니다.",
                empathy_message="다른 사람을 챙기느라 정작 자신의 감정을 놓치고 있진 않나요? 당신의 마음도 소중해요.",
                color_hint="purple",
            ))

        return ReportSection(
            title="당신의 성격 프로파일",
            summary=self._big_five_summary(bf),
            icon="personality",
            color="blue",
            insights=insights,
        )

    def _multi_variable_personality(self, bf) -> list[InsightItem]:
        """다변수 조합 인사이트 - 두 가지 이상 특성의 상호작용"""
        insights = []

        # 외향 + 신경성 높음 = 외부 표출형 불안
        if bf.extraversion > 60 and bf.neuroticism > 60:
            insights.append(InsightItem(
                title="활발하지만 내면은 불안한 사람",
                description="사람들 사이에서 에너지를 얻지만, 동시에 관계에서 상처받기도 쉽습니다. "
                            "활발한 모습 뒤에 불안이 숨어 있을 수 있어요.",
                empathy_message="밖에서는 괜찮은 척하고 집에 오면 지치는 날이 있지 않나요? 그 피로감은 진짜예요.",
                priority=InsightPriority.PRIMARY,
                color_hint="yellow",
            ))

        # 내향 + 친화성 높음 = 피플플리저
        if bf.extraversion < 40 and bf.agreeableness > 65:
            insights.append(InsightItem(
                title="조용히 맞춰주는 사람",
                description="혼자 있는 것이 편하지만 다른 사람의 기대에 맞추려 애씁니다. "
                            "거절하기 어려워 자신의 필요를 뒤로 미루는 패턴이 있을 수 있어요.",
                empathy_message="'아니오'라고 말하는 것은 나쁜 게 아니에요. 당신의 에너지는 유한하니까요.",
                priority=InsightPriority.PRIMARY,
                color_hint="purple",
            ))

        # 성실성 + 신경성 높음 = 완벽주의 번아웃
        if bf.conscientiousness > 65 and bf.neuroticism > 60:
            insights.append(InsightItem(
                title="완벽을 추구하지만 지치는 사람",
                description="높은 기준을 세우고 열심히 하지만, 동시에 '충분하지 않다'는 불안이 따라옵니다. "
                            "이 긴장이 번아웃의 원인이 될 수 있어요.",
                empathy_message="이미 충분히 잘하고 있어요. 80%도 괜찮다는 것을 스스로에게 말해주세요.",
                priority=InsightPriority.PRIMARY,
                color_hint="yellow",
            ))

        # 개방성 높음 + 성실성 낮음 = 자유로운 영혼
        if bf.openness > 65 and bf.conscientiousness < 40:
            insights.append(InsightItem(
                title="자유롭지만 때로 방향을 잃는 사람",
                description="새로운 것에 끌리지만, 하나에 집중하기 어려울 수 있습니다. "
                            "많은 가능성 앞에서 오히려 선택이 어려워질 때가 있어요.",
                empathy_message="모든 걸 다 하지 않아도 괜찮아요. 지금 가장 끌리는 하나에 집중해보세요.",
                priority=InsightPriority.PRIMARY,
                color_hint="blue",
            ))

        # 친화성 낮음 + 성실성 높음 = 원칙주의자
        if bf.agreeableness < 40 and bf.conscientiousness > 65:
            insights.append(InsightItem(
                title="원칙을 중시하는 독립적인 사람",
                description="자신만의 기준이 명확하고, 그에 따라 행동합니다. "
                            "때로는 주변 사람들이 당신을 차갑게 느낄 수 있지만, 그건 당신의 진심이 아닐 거예요.",
                empathy_message="기준이 있다는 건 강점이에요. 다만 가끔은 기준을 내려놓고 그냥 함께해보는 것도 괜찮아요.",
                priority=InsightPriority.PRIMARY,
                color_hint="green",
            ))

        return insights

    # ──── 애착 섹션 (스펙트럼 기반) ────

    def _attachment_section(self, at, bf) -> ReportSection:
        insights = []

        # 스펙트럼 기반 주요 인사이트
        if at.is_mixed:
            insights.append(InsightItem(
                title=f"복합적인 관계 패턴: {at.blend_description}",
                description="당신의 애착 유형은 하나로 정의하기 어렵습니다. "
                            "상황과 상대에 따라 다른 모습이 나타날 수 있어요. "
                            "이것은 나쁜 것이 아니라, 그만큼 다양한 관계 경험을 해왔다는 뜻이에요.",
                empathy_message="복잡한 것은 풍부한 것이에요. 자신의 패턴을 인식하는 것만으로도 큰 한 걸음입니다.",
                priority=InsightPriority.PRIMARY,
                color_hint="purple",
            ))
        else:
            dominant = at.dominant_type
            templates = {
                "안정형": InsightItem(
                    title="안정적인 관계를 맺는 사람",
                    description="당신은 관계에서 신뢰를 기반으로 편안함을 느끼고, 상대에게 적절한 거리와 친밀함을 유지할 수 있습니다.",
                    empathy_message="당신의 이런 안정감은 주변 사람들에게도 큰 힘이 됩니다.",
                    color_hint="green",
                ),
                "불안형": InsightItem(
                    title="사랑받고 싶은 마음이 큰 사람",
                    description="당신은 관계에서 상대의 반응에 민감하고, 거절당할까 봐 걱정하는 경향이 있습니다.",
                    empathy_message="그건 당신이 사랑에 진심이기 때문이에요. 하지만 상대의 모든 반응이 당신에 대한 평가는 아니에요.",
                    color_hint="pink",
                ),
                "회피형": InsightItem(
                    title="독립적인 공간이 필요한 사람",
                    description="당신은 관계에서 거리를 유지하고 싶어하고, 깊은 감정적 교류가 부담스러울 수 있습니다.",
                    empathy_message="자신을 보호하는 것도 중요하지만, 때로는 마음의 문을 열어보는 것도 괜찮아요.",
                    color_hint="blue",
                ),
            }
            insights.append(templates[dominant])

        # 애착 + Big Five 상호작용 인사이트
        interaction_insights = self._attachment_bigfive_interactions(at, bf)
        insights.extend(interaction_insights)

        # 긴장 쌍이 있으면 표시
        tension = at.tension_pair
        if tension:
            insights.append(InsightItem(
                title=f"내면의 갈등: {tension[0]}과 {tension[1]} 사이",
                description=f"당신 안에는 {tension[0]}과 {tension[1]}의 성향이 공존합니다. "
                            f"가까워지고 싶으면서도 거리를 두고 싶은 마음, 둘 다 진짜 당신이에요.",
                empathy_message="이런 갈등은 많은 사람들이 경험합니다. 어느 쪽이 '진짜 나'인지 고민하지 않아도 돼요.",
                priority=InsightPriority.TENSION,
                color_hint="yellow",
            ))

        spectrum = at.spectrum
        summary_parts = []
        for type_name, level in spectrum.items():
            if level == "high":
                summary_parts.append(f"{type_name} 성향이 높음")
            elif level == "mid":
                summary_parts.append(f"{type_name} 성향이 보통")

        summary = ", ".join(summary_parts) if summary_parts else f"주요 애착 유형: {at.dominant_type}"

        return ReportSection(
            title="당신의 관계 패턴",
            summary=summary,
            icon="relationship",
            color="pink",
            insights=insights,
        )

    def _attachment_bigfive_interactions(self, at, bf) -> list[InsightItem]:
        """애착 유형과 Big Five의 상호작용 인사이트"""
        insights = []

        # 회피형 + 성실성 높음 = 자립형 워커홀릭
        if at.avoidant >= 60 and bf.conscientiousness > 65:
            insights.append(InsightItem(
                title="일에 몰두하는 독립적인 사람",
                description="관계보다 일이나 목표에 집중하는 경향이 있습니다. "
                            "이것은 당신의 강점이지만, 때로는 관계가 뒷전이 될 수 있어요.",
                empathy_message="성취도 중요하지만, 곁에 있는 사람도 당신만큼 중요해요.",
                priority=InsightPriority.PRIMARY,
                color_hint="green",
            ))

        # 불안형 + 내향 = 내면 반추
        if at.anxious >= 60 and bf.extraversion < 40:
            insights.append(InsightItem(
                title="마음속으로 많이 생각하는 사람",
                description="관계에서 불안을 느끼지만 밖으로 표현하기보다 혼자 끙끙 앓는 편입니다. "
                            "머릿속에서 상대의 말과 행동을 반복 재생하곤 해요.",
                empathy_message="생각이 꼬리를 물 때, '지금 이 순간'에 집중해보세요. 상상 속의 시나리오는 대부분 일어나지 않아요.",
                priority=InsightPriority.PRIMARY,
                color_hint="yellow",
            ))

        # 불안형 + 친화성 높음 = 과도한 배려
        if at.anxious >= 60 and bf.agreeableness > 65:
            insights.append(InsightItem(
                title="상대를 위해 자신을 잊는 사람",
                description="사랑받기 위해 상대에게 과도하게 맞추는 패턴이 있을 수 있습니다. "
                            "그 배려가 당신을 지치게 만들고 있지는 않나요?",
                empathy_message="당신이 주는 만큼 받을 자격이 있어요. 관계는 일방통행이 아니에요.",
                priority=InsightPriority.PRIMARY,
                color_hint="pink",
            ))

        return insights

    # ──── 사랑 섹션 ────

    def _love_section(self, lt) -> ReportSection:
        love_type = lt.love_type
        insights = []

        desc_map = {
            "완전한 사랑": ("친밀감, 열정, 헌신이 모두 균형 잡힌 이상적인 사랑의 형태입니다.",
                          "이 균형을 유지하려면 의식적인 노력이 필요해요. 당연하다고 생각하지 말고 가꾸어주세요."),
            "낭만적 사랑": ("깊은 친밀감과 강한 열정이 특징입니다. 지금은 아름답지만, 장기적 약속이 뒷받침되면 더 단단해질 수 있어요.",
                          "설렘도 중요하지만, '함께 할 미래'에 대한 대화도 필요한 시점일 수 있어요."),
            "우애적 사랑": ("깊은 친밀감과 헌신이 특징인, 단단한 동반자적 사랑입니다.",
                          "안정적이지만, 때로는 작은 설렘을 불어넣어 주세요. 새로운 경험을 함께하면 열정이 돌아올 수 있어요."),
            "맹목적 사랑": ("강한 열정과 헌신이 있지만, 서로를 깊이 이해하는 시간이 더 필요할 수 있습니다.",
                          "설렘에 취해 있지 않나요? 상대를 '알아가는' 시간을 의식적으로 만들어보세요."),
            "좋아함": ("친밀감이 중심인, 따뜻하고 편안한 관계입니다.",
                     "좋은 관계의 기반이에요. 여기에 작은 설렘과 약속을 더하면 사랑이 깊어질 수 있어요."),
            "도취적 사랑": ("열정이 중심인 관계로, 강렬하지만 불안정할 수 있습니다.",
                         "설렘은 시간이 지나면 자연스럽게 변합니다. 친밀감을 쌓아가면 더 풍요로운 관계가 될 거예요."),
            "공허한 사랑": ("헌신은 있지만 친밀감과 열정이 부족한 관계일 수 있습니다.",
                         "의무감으로 관계를 유지하고 있지는 않나요? 서로의 감정을 솔직하게 나눠보세요."),
            "탐색 중": ("아직 사랑의 요소를 충분히 경험하지 못한 상태일 수 있습니다.",
                      "괜찮아요. 사랑은 준비된 사람에게 찾아옵니다. 먼저 자신을 사랑하는 연습부터 해보세요."),
        }

        desc, guidance = desc_map.get(love_type, ("", ""))
        insights.append(InsightItem(
            title=f"당신의 사랑 유형: {love_type}",
            description=desc,
            empathy_message=guidance,
            priority=InsightPriority.PRIMARY,
            color_hint="pink",
        ))

        # 강점/약점 안내
        insights.append(InsightItem(
            title=f"가장 강한 사랑의 요소: {lt.strongest}",
            description=f"당신은 관계에서 {lt.strongest}을 가장 중요하게 여기고, 잘 표현합니다.",
            empathy_message=f"반면 {lt.weakest}은 상대적으로 낮은 편이에요. 이 부분을 의식적으로 채워보는 건 어떨까요?",
            color_hint="purple",
        ))

        return ReportSection(
            title="당신의 사랑 스타일",
            summary=f"당신의 사랑 유형은 '{love_type}'이며, {lt.strongest}이 가장 강합니다.",
            icon="love",
            color="pink",
            insights=insights,
        )

    # ──── 모순/갈등 인사이트 ────

    def _generate_tensions(self, bf, at, lt) -> list[InsightItem]:
        """심리적 모순이나 갈등을 현실적으로 드러내는 인사이트"""
        tensions = []

        # 친밀감 높은데 회피형
        if lt.intimacy > 60 and at.avoidant > 55:
            tensions.append(InsightItem(
                title="가까워지고 싶지만 거리를 두는 마음",
                description="관계에서 친밀함을 원하면서도 막상 가까워지면 부담을 느낍니다. "
                            "이 갈등은 과거의 상처에서 비롯되었을 수 있어요.",
                empathy_message="두 마음 모두 진짜 당신이에요. 작은 한 걸음씩, 안전한 속도로 가까워져도 괜찮아요.",
                priority=InsightPriority.TENSION,
                color_hint="yellow",
            ))

        # 친화성 높은데 불안형
        if bf.agreeableness > 65 and at.anxious > 60:
            tensions.append(InsightItem(
                title="맞추느라 지치는 사람",
                description="상대의 기분을 맞추려 애쓰면서, 내가 사랑받고 있는지 불안해합니다. "
                            "이 패턴이 반복되면 관계에서 점점 자신을 잃게 될 수 있어요.",
                empathy_message="상대의 사랑을 확인하기 위해 자신을 바꾸지 않아도 돼요. 있는 그대로의 당신도 충분히 사랑받을 수 있어요.",
                priority=InsightPriority.TENSION,
                color_hint="pink",
            ))

        # 개방성 높은데 성실성도 높음
        if bf.openness > 65 and bf.conscientiousness > 65:
            tensions.append(InsightItem(
                title="자유롭고 싶지만 책임감도 강한 사람",
                description="새로운 것을 시도하고 싶으면서도 기존의 약속과 책임을 져버리기 어렵습니다. "
                            "이 긴장 속에서 때로 스스로를 옥죄고 있을 수 있어요.",
                empathy_message="모든 걸 다 하려고 하지 않아도 돼요. 때로는 '충분히 잘하고 있다'고 자신에게 말해주세요.",
                priority=InsightPriority.TENSION,
                color_hint="blue",
            ))

        # 외향성 낮은데 불안형
        if bf.extraversion < 40 and at.anxious > 60:
            tensions.append(InsightItem(
                title="말하고 싶지만 말할 수 없는 마음",
                description="관계에서 불안을 느끼지만, 그걸 표현하기가 어렵습니다. "
                            "혼자 끙끙 앓다가 결국 터지거나, 아니면 그냥 참는 패턴이 반복될 수 있어요.",
                empathy_message="감정을 표현하는 것은 연습이 필요해요. 작은 것부터, 안전한 사람에게 시작해보세요.",
                priority=InsightPriority.TENSION,
                color_hint="yellow",
            ))

        return tensions

    # ──── 요약/위로/팁 생성 ────

    def _big_five_summary(self, bf) -> str:
        traits = []
        if bf.extraversion > 60:
            traits.append("사교적이고")
        elif bf.extraversion < 40:
            traits.append("내성적이며")
        if bf.openness > 60:
            traits.append("호기심이 많고")
        if bf.conscientiousness > 60:
            traits.append("계획적이며")
        if bf.agreeableness > 60:
            traits.append("따뜻하고")
        if bf.neuroticism > 60:
            traits.append("감정이 섬세한")

        if not traits:
            return "당신은 균형 잡힌 성격을 가진 사람입니다."
        return f"당신은 {' '.join(traits)} 사람입니다."

    def _generate_summary(self, bf, at) -> str:
        base = self._big_five_summary(bf)
        attachment_desc = {
            "안정형": "관계에서 안정감을 주는",
            "불안형": "사랑에 진심인",
            "회피형": "독립적이고 자유로운",
        }
        if at.is_mixed:
            at_desc = "관계에서 복합적인 모습을 보이는"
        else:
            at_desc = attachment_desc.get(at.dominant_type, "")
        return f"{base} 그리고 {at_desc} 사람이기도 합니다."

    def _generate_struggle(self, bf, at) -> str:
        reasons = []
        if bf.neuroticism > 60:
            reasons.append("감정의 파도가 높아서 쉽게 지칠 수 있습니다")
        if bf.agreeableness > 70:
            reasons.append("다른 사람의 감정을 너무 많이 짊어지고 있을 수 있습니다")
        if at.dominant_type == "불안형":
            reasons.append("상대의 반응에 너무 많은 의미를 부여하고 있을 수 있습니다")
        if at.dominant_type == "회피형":
            reasons.append("마음을 열기 어려워서 진짜 원하는 것을 얻지 못하고 있을 수 있습니다")
        if bf.conscientiousness > 70:
            reasons.append("스스로에게 너무 높은 기준을 세우고 있을 수 있습니다")
        if at.tension_pair:
            t = at.tension_pair
            reasons.append(f"내면에서 {t[0]}과 {t[1]}이 충돌하고 있을 수 있습니다")

        if not reasons:
            return "당신은 전반적으로 안정적인 심리 상태를 보이고 있습니다. 하지만 누구나 힘든 순간이 있죠."

        return "당신이 힘든 이유는… " + ". 그리고 ".join(reasons) + "."

    def _generate_comfort(self, bf, at) -> str:
        if at.is_mixed and at.tension_pair:
            return ("상반된 마음이 공존하는 것은 당신이 깊은 사람이라는 뜻이에요. "
                    "어느 한쪽이 '진짜 나'인지 고민하지 않아도 됩니다. "
                    "두 마음 모두 당신이고, 그 복잡함 속에서도 당신은 충분합니다.")
        if at.dominant_type == "불안형":
            return ("당신은 사랑받기 위해 노력하는 것이 아니라, 이미 사랑받을 자격이 있는 사람입니다. "
                    "상대의 침묵이 당신에 대한 거부가 아닐 수 있다는 것을 기억해주세요.")
        if at.dominant_type == "회피형":
            return ("혼자 있는 것이 편하다고 느끼는 것은 괜찮아요. "
                    "하지만 가끔은 누군가에게 기대도 된다는 것을 알아주세요. 당신은 충분히 그럴 자격이 있습니다.")
        if bf.neuroticism > 60:
            return ("감정이 요동치는 날들이 있어도 괜찮아요. "
                    "그건 당신이 세상을 깊이 느끼는 사람이라는 증거입니다. "
                    "지금 이 순간, 당신은 충분히 잘하고 있습니다.")
        return ("당신은 이미 충분합니다. "
                "완벽하지 않아도, 모든 것을 다 해내지 않아도 괜찮아요. "
                "지금의 당신 그대로가 가장 좋습니다.")

    def _generate_tips(self, bf, at, lt) -> list[str]:
        """프로파일에 정합하는 행동 팁"""
        tips = []

        # 신경성 높고 + 내향적이면 → 혼자 할 수 있는 활동
        if bf.neuroticism > 60 and bf.extraversion < 40:
            tips.append("하루 5분, 종이에 감정을 적어보세요. 말하기 어려운 것도 글로는 쉬울 수 있어요.")
        elif bf.neuroticism > 60:
            tips.append("신뢰하는 한 사람에게 오늘 느낀 감정 하나만 이야기해보세요.")

        # 불안형 + 친화성 높으면 → 경계 설정 연습
        if at.dominant_type == "불안형" and bf.agreeableness > 65:
            tips.append("이번 주 한 번만 '나는 이렇게 느꼈어'라고 솔직하게 말해보세요. 맞추기보다 표현하기.")
        elif at.dominant_type == "불안형":
            tips.append("상대의 반응에 해석을 덧붙이기 전에, '사실'만 먼저 확인해보세요.")

        # 회피형 + 성실성 높으면 → 관계에 시간 할애
        if at.dominant_type == "회피형" and bf.conscientiousness > 65:
            tips.append("일정표에 '관계를 위한 시간'을 의식적으로 넣어보세요. 일처럼 관리하면 더 편할 수 있어요.")
        elif at.dominant_type == "회피형":
            tips.append("하루에 한 번, '오늘 좋았어'같은 작은 감정 표현을 해보세요.")

        if bf.agreeableness > 70 and at.dominant_type != "불안형":
            tips.append("이번 주에 한 번, 작은 부탁을 정중하게 거절해보세요. '아니오'도 괜찮은 대답이에요.")

        if bf.conscientiousness > 70:
            tips.append("일부러 계획 없는 시간을 만들어보세요. 예상 밖의 즐거움을 발견할 수 있어요.")

        if lt.passion < 40 and lt.intimacy > 60:
            tips.append("파트너와 새로운 경험을 함께 해보세요. 작은 변화가 설렘을 다시 불러올 수 있어요.")

        if not tips:
            tips.append("자신의 감정을 소중히 여기고, 때로는 멈춰서 쉬어가세요.")
        return tips

    def _generate_action_plan(self, bf, at, lt) -> list[ActionStep]:
        """4주 행동 계획"""
        steps = []

        # 1주차: 자기 인식
        if bf.neuroticism > 60:
            steps.append(ActionStep(week=1, action="하루 한 번, 지금 느끼는 감정에 이름 붙이기",
                                   reason="감정을 인식하는 것만으로도 그 강도가 줄어듭니다."))
        else:
            steps.append(ActionStep(week=1, action="하루 끝에 '오늘 가장 좋았던 순간' 하나 떠올리기",
                                   reason="긍정적 경험에 주의를 기울이면 전반적인 만족감이 높아집니다."))

        # 2주차: 관계
        if at.dominant_type == "불안형":
            steps.append(ActionStep(week=2, action="상대에게 확인하고 싶을 때, 5분만 기다려보기",
                                   reason="충동적인 확인 대신 기다림이 불안을 줄여줍니다."))
        elif at.dominant_type == "회피형":
            steps.append(ActionStep(week=2, action="소중한 사람에게 '고마워'를 직접 말하기",
                                   reason="작은 표현이 관계의 온도를 바꿉니다."))
        else:
            steps.append(ActionStep(week=2, action="소중한 사람과 30분 이상 집중 대화하기",
                                   reason="관계는 시간을 투자할 때 깊어집니다."))

        # 3주차: 행동
        if bf.conscientiousness > 65:
            steps.append(ActionStep(week=3, action="이번 주 하나의 계획을 의도적으로 바꿔보기",
                                   reason="유연함을 연습하면 예상 밖의 기회를 발견할 수 있어요."))
        else:
            steps.append(ActionStep(week=3, action="작은 목표 하나를 세우고 달성해보기",
                                   reason="성취 경험이 자신감을 키워줍니다."))

        # 4주차: 성장
        steps.append(ActionStep(week=4, action="이 테스트를 다시 해보고 변화를 확인하기",
                               reason="자기 인식의 변화를 추적하면 성장의 동기가 됩니다."))

        return steps

"""내러티브 엔진 - 결과 문장 생성 (공감 + 해석 + 선택지)"""

from __future__ import annotations

from ..models.user_profile import UserProfile
from ..models.result import PersonalReport, ReportSection, InsightItem


class NarrativeEngine:
    """심리 프로파일을 기반으로 공감형 결과 리포트를 생성"""

    def generate_report(self, profile: UserProfile) -> PersonalReport:
        bf = profile.big_five
        at = profile.attachment
        lt = profile.love_triangle

        sections = [
            self._personality_section(bf),
            self._attachment_section(at),
            self._love_section(lt),
        ]

        return PersonalReport(
            profile_summary=self._generate_summary(bf, at),
            struggle_reason=self._generate_struggle(bf, at),
            comfort_message=self._generate_comfort(bf, at),
            sections=sections,
            action_tips=self._generate_tips(bf, at, lt),
        )

    def _personality_section(self, bf) -> ReportSection:
        insights = []

        # 외향성
        if bf.extraversion > 65:
            insights.append(InsightItem(
                title="사람과의 연결에서 에너지를 얻는 사람",
                description="당신은 사람들과 함께할 때 활력을 느끼고, 새로운 만남에서 즐거움을 찾습니다.",
                empathy_message="그래서 혼자 있는 시간이 길어지면 조금 답답하게 느껴질 수 있어요.",
            ))
        elif bf.extraversion < 35:
            insights.append(InsightItem(
                title="내면의 세계가 풍부한 사람",
                description="당신은 혼자만의 시간에서 에너지를 충전하고, 깊은 생각과 내면의 대화를 즐깁니다.",
                empathy_message="사교적이지 않다고 해서 사람을 싫어하는 게 아니에요. 단지 당신만의 방식으로 세상과 연결되는 것뿐이에요.",
            ))

        # 신경성
        if bf.neuroticism > 65:
            insights.append(InsightItem(
                title="감정이 섬세한 사람",
                description="당신은 감정의 변화를 크게 느끼고, 작은 것에도 깊이 반응합니다.",
                empathy_message="그게 때로는 힘들 수 있지만, 그만큼 세상을 깊이 느낄 수 있는 능력이기도 해요.",
            ))
        elif bf.neuroticism < 35:
            insights.append(InsightItem(
                title="감정적으로 안정된 사람",
                description="당신은 스트레스 상황에서도 비교적 평온함을 유지할 수 있습니다.",
                empathy_message="때로는 감정을 너무 억누르고 있진 않은지 스스로에게 물어보는 것도 좋아요.",
            ))

        # 개방성
        if bf.openness > 65:
            insights.append(InsightItem(
                title="새로운 경험에 열린 사람",
                description="당신은 호기심이 많고, 익숙하지 않은 것에도 도전하는 것을 즐깁니다.",
                empathy_message="늘 새로운 것을 찾아 떠나는 당신, 때로는 지금 있는 곳에서 머무는 것도 괜찮아요.",
            ))

        # 성실성
        if bf.conscientiousness > 65:
            insights.append(InsightItem(
                title="계획적이고 책임감 있는 사람",
                description="당신은 목표를 세우고 꾸준히 노력하는 것을 중요하게 여깁니다.",
                empathy_message="항상 완벽해야 한다는 압박을 느끼고 있지는 않나요? 가끔은 계획 없이 흘러가는 것도 좋아요.",
            ))

        # 친화성
        if bf.agreeableness > 65:
            insights.append(InsightItem(
                title="타인을 먼저 생각하는 따뜻한 사람",
                description="당신은 다른 사람의 감정에 공감하고, 조화를 중요하게 여깁니다.",
                empathy_message="다른 사람을 챙기느라 정작 자신의 감정을 놓치고 있진 않나요? 당신의 마음도 소중해요.",
            ))

        return ReportSection(
            title="당신의 성격 프로파일",
            summary=self._big_five_summary(bf),
            insights=insights,
        )

    def _attachment_section(self, at) -> ReportSection:
        dominant = at.dominant_type
        insights = []

        templates = {
            "안정형": InsightItem(
                title="안정적인 관계를 맺는 사람",
                description="당신은 관계에서 신뢰를 기반으로 편안함을 느끼고, 상대에게 적절한 거리와 친밀함을 유지할 수 있습니다.",
                empathy_message="당신의 이런 안정감은 주변 사람들에게도 큰 힘이 됩니다.",
            ),
            "불안형": InsightItem(
                title="사랑받고 싶은 마음이 큰 사람",
                description="당신은 관계에서 상대의 반응에 민감하고, 거절당할까 봐 걱정하는 경향이 있습니다.",
                empathy_message="그건 당신이 사랑에 진심이기 때문이에요. 하지만 상대의 모든 반응이 당신에 대한 평가는 아니에요.",
            ),
            "회피형": InsightItem(
                title="독립적인 공간이 필요한 사람",
                description="당신은 관계에서 거리를 유지하고 싶어하고, 깊은 감정적 교류가 부담스러울 수 있습니다.",
                empathy_message="자신을 보호하는 것도 중요하지만, 때로는 마음의 문을 열어보는 것도 괜찮아요. 당신은 충분히 사랑받을 자격이 있으니까요.",
            ),
        }

        insights.append(templates[dominant])

        return ReportSection(
            title="당신의 관계 패턴",
            summary=f"당신의 주요 애착 유형은 '{dominant}'입니다.",
            insights=insights,
        )

    def _love_section(self, lt) -> ReportSection:
        love_type = lt.love_type
        insights = []

        desc_map = {
            "완전한 사랑": "친밀감, 열정, 헌신이 모두 균형 잡힌 이상적인 사랑의 형태입니다.",
            "낭만적 사랑": "깊은 친밀감과 강한 열정이 특징입니다. 감정적으로 깊이 연결되어 있습니다.",
            "우애적 사랑": "친밀감과 헌신이 특징인, 깊은 우정과 같은 사랑입니다.",
            "맹목적 사랑": "강한 열정과 헌신이 특징이지만, 깊은 이해가 부족할 수 있습니다.",
            "좋아함": "친밀감이 중심인, 따뜻하고 편안한 관계를 추구합니다.",
            "도취적 사랑": "열정이 중심인, 강렬하지만 불안정할 수 있는 관계입니다.",
            "공허한 사랑": "헌신은 있지만 친밀감과 열정이 부족한 관계입니다.",
            "비사랑": "아직 사랑의 요소를 충분히 경험하지 못한 상태일 수 있습니다.",
        }

        insights.append(InsightItem(
            title=f"당신의 사랑 유형: {love_type}",
            description=desc_map.get(love_type, ""),
            empathy_message="어떤 유형이든 '틀린' 사랑은 없습니다. 중요한 것은 나와 상대가 서로의 필요를 이해하는 것이에요.",
        ))

        return ReportSection(
            title="당신의 사랑 스타일",
            summary=f"당신의 사랑 유형은 '{love_type}'입니다.",
            insights=insights,
        )

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

        if not reasons:
            return "당신은 전반적으로 안정적인 심리 상태를 보이고 있습니다. 하지만 누구나 힘든 순간이 있죠."

        return "당신이 힘든 이유는… " + ". 그리고 ".join(reasons) + "."

    def _generate_comfort(self, bf, at) -> str:
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
        tips = []
        if bf.neuroticism > 60:
            tips.append("하루 5분, 감정 일기를 써보세요. 감정을 이름 붙이는 것만으로도 마음이 가벼워집니다.")
        if at.dominant_type == "불안형":
            tips.append("상대의 반응에 해석을 덧붙이기 전에, '사실'만 먼저 확인해보세요.")
        if at.dominant_type == "회피형":
            tips.append("하루에 한 번, 작은 감정이라도 상대에게 표현해보세요. '오늘 좋았어'라는 말 한마디면 충분합니다.")
        if bf.agreeableness > 70:
            tips.append("'아니오'라고 말하는 연습을 해보세요. 당신의 필요도 중요합니다.")
        if bf.conscientiousness > 70:
            tips.append("계획 없는 하루를 일부러 만들어보세요. 예상 밖의 즐거움을 발견할 수 있습니다.")
        if lt.passion < 40 and lt.intimacy > 60:
            tips.append("관계에 작은 변화를 주어보세요. 새로운 경험을 함께하면 설렘이 다시 찾아올 수 있습니다.")
        if not tips:
            tips.append("자신의 감정을 소중히 여기고, 때로는 멈춰서 쉬어가세요.")
        return tips

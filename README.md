# Miromi

> "나를 비추는 거울, 당신을 이해하게 만드는 앱"

**심리학 기반 자기이해 + 관계 개선 도구**

## 컨셉

Miromi는 검증된 심리학 이론을 UX로 번역한 자기이해 앱입니다.
단순 심리 테스트가 아닌, 스토리형 진행을 통해 사용자가 자신을 깊이 이해하고
관계를 개선할 수 있도록 돕습니다.

## 심리학적 기반

| 이론 | 역할 | 활용 |
|------|------|------|
| **Big Five** (성격 5요인) | 성격 구조의 기본 축 | 외향성/신경성/성실성/개방성/친화성 프로파일 |
| **Johari Window** | 자기인식 확장 | 내가 모르는 나를 드러내는 장치 |
| **Attachment Theory** (애착이론) | 관계 패턴 해석 | 안정형/회피형/불안형 분류 |
| **Sternberg's Triangle** (사랑의 삼각이론) | 커플 궁합 분석 | 친밀감/열정/헌신 기반 관계 유형 |

## 제품 구조

### Phase 1: "나를 찾아 떠나는 여행"
- 감정 상태 체크 → 가치관 → 행동 패턴 → 관계 스타일 → 과거 경험
- 스토리형 진행 (숲 속 여행 메타포)
- 결과: 심리 프로파일 + 위로 메시지

### Phase 2: "연인을 알자"
- 서로 질문 답변 (비공개) → 결과 비교
- 차이 분석 / 궁합 분석 / 대화 가이드 자동 생성

## 기술 아키텍처

```
├── lib/
│   ├── engines/
│   │   ├── question_engine.py    # 질문 관리 및 흐름 제어
│   │   ├── scoring_engine.py     # Big Five / Attachment 점수 계산
│   │   ├── narrative_engine.py   # 결과 문장 생성 (스토리텔링)
│   │   └── match_engine.py       # 두 사람 비교 (Phase 2)
│   ├── models/
│   │   ├── user_profile.py       # 사용자 심리 프로파일
│   │   ├── question.py           # 질문 모델
│   │   └── result.py             # 결과 리포트 모델
│   ├── data/
│   │   └── questions.json        # 질문 데이터셋 (50문항)
│   └── utils/
│       └── helpers.py            # 유틸리티 함수
├── tests/
│   ├── test_scoring.py
│   └── test_narrative.py
└── docs/
    └── psychology_references.md
```

## 차별화 포인트

1. **스토리형 진행** - 질문이 아닌 여행, 몰입감 극대화
2. **상황 기반 질문** - "외향적인가?" (X) → "모임에서 먼저 말을 거는 편인가?" (O)
3. **공감형 결과** - 단정/평가 없이, 공감 + 해석 + 선택지 제공
4. **대화 가이드** - 분석에서 끝나지 않고 실제 관계 개선 도구 제공

## 수익 모델

- **무료**: 기본 분석
- **프리미엄**: 상세 리포트 / 커플 분석 / AI 상담 리포트

## 설치 및 실행

```bash
pip install -r requirements.txt
python -m lib.engines.question_engine
```

## 라이선스

MIT License

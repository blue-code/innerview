"""InnerView CLI - 터미널에서 심리 여행 체험"""

from __future__ import annotations

import sys
import uuid

from lib.engines.question_engine import QuestionEngine
from lib.engines.scoring_engine import ScoringEngine
from lib.engines.narrative_engine import NarrativeEngine
from lib.engines.couple_game_engine import CoupleGameEngine
from lib.db import Database


def clear_line():
    print()


def print_header(text: str):
    width = 50
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width)


def print_narrative(text: str):
    print(f"\n  {text}")


def print_progress(current: int, total: int):
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\n  [{bar}] {current}/{total}")


def get_choice(num_choices: int) -> int:
    while True:
        try:
            choice = input("\n  선택 > ").strip()
            idx = int(choice) - 1
            if 0 <= idx < num_choices:
                return idx
            print(f"  1~{num_choices} 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("  숫자를 입력해주세요.")
        except (EOFError, KeyboardInterrupt):
            print("\n\n  여행을 중단합니다.")
            sys.exit(0)


def run_phase1():
    """Phase 1: 나를 찾아 떠나는 여행"""
    print_header("InnerView - 나를 찾아 떠나는 여행")
    print("\n  당신을 이해하기 위한 여행을 시작합니다.")
    print("  각 질문에 솔직하게 답해주세요.")
    print("  정답은 없습니다. 당신의 마음이 정답입니다.\n")

    input("  [Enter를 눌러 여행을 시작하세요] ")

    engine = QuestionEngine(phase=1)
    scoring = ScoringEngine()
    db = Database()
    user_id = str(uuid.uuid4())[:8]
    db.create_user(user_id, "여행자")

    while not engine.is_complete:
        q = engine.current_question()
        if q is None:
            break

        print_progress(engine.current_index + 1, engine.total)
        print_narrative(q.narrative)
        print(f"\n  Q. {q.question}\n")

        for i, choice in enumerate(q.choices):
            print(f"    {i + 1}. {choice.text}")

        idx = get_choice(len(q.choices))
        scores = engine.answer(idx)
        scoring.add_scores(scores)
        db.save_answer(user_id, q.id, idx)

    # 결과 생성
    profile = scoring.build_profile(user_id)
    db.save_profile(profile)

    narrative = NarrativeEngine()
    report = narrative.generate_report(profile)

    # 결과 출력
    print_header("여행이 끝났습니다")
    print(f"\n  {report.profile_summary}")

    for section in report.sections:
        print(f"\n  --- {section.title} ---")
        print(f"  {section.summary}")
        for insight in section.insights:
            print(f"\n    [{insight.title}]")
            print(f"    {insight.description}")
            print(f"    → {insight.empathy_message}")

    print(f"\n  --- 당신이 힘든 이유 ---")
    print(f"  {report.struggle_reason}")

    print(f"\n  --- 당신을 위한 메시지 ---")
    print(f"  {report.comfort_message}")

    if report.action_tips:
        print(f"\n  --- 오늘부터 할 수 있는 것 ---")
        for i, tip in enumerate(report.action_tips, 1):
            print(f"    {i}. {tip}")

    print("\n" + "=" * 50)
    print("  당신의 여행 결과가 저장되었습니다.")
    print("=" * 50 + "\n")

    return user_id, profile


def run_couple_game():
    """Phase 2: 커플 게임"""
    print_header("InnerView - 커플 게임")
    print("\n  둘이 함께 하는 관계 탐험 게임입니다!")
    print("  서로를 얼마나 알고 있는지 확인해보세요.\n")

    name_a = input("  플레이어 1 이름 > ").strip() or "A"
    name_b = input("  플레이어 2 이름 > ").strip() or "B"

    game_engine = CoupleGameEngine()
    session = game_engine.create_session(name_a, name_b)
    db = Database()
    db.create_user(name_a, name_a)
    db.create_user(name_b, name_b)

    print("\n  게임을 선택하세요:\n")
    print("    1. 예측 게임 - 상대의 선택을 맞춰보세요")
    print("    2. 밸런스 게임 - 싱크로율 체크!")
    print("    3. 시크릿 카드 - 서로에게 비밀 메시지")
    print("    4. 챌린지 미션 - 관계 개선 미션")
    print("    5. 전체 게임 (모두 플레이)")

    game_choice = get_choice(5)

    if game_choice == 0 or game_choice == 4:
        _play_predict(game_engine, session, name_a, name_b, db)
    if game_choice == 1 or game_choice == 4:
        _play_balance(game_engine, session, name_a, name_b, db)
    if game_choice == 2 or game_choice == 4:
        _play_secret_cards(game_engine, session, name_a, name_b)
    if game_choice == 3 or game_choice == 4:
        _play_challenges(game_engine, session)

    # 최종 결과
    print_header("커플 게임 결과!")
    print(f"\n  커플 레벨: {session.couple_level}")
    print(f"  싱크로율 등급: {session.sync_grade}")
    print(f"  커플 칭호: {game_engine.generate_couple_title(session)}")
    print(f"\n  {name_a} 포인트: {session.score_a}")
    print(f"  {name_b} 포인트: {session.score_b}")
    print("\n" + "=" * 50 + "\n")


def _play_predict(engine: CoupleGameEngine, session, name_a: str, name_b: str, db: Database):
    """예측 게임"""
    print_header("예측 게임 - 상대의 마음을 읽어라!")
    print("  상대방이 어떤 선택을 할지 맞춰보세요.\n")

    questions = engine.get_predict_questions(4)

    for q in questions:
        print(f"\n  상황: {q.situation}")
        print(f"  Q. {q.question}\n")
        for i, c in enumerate(q.choices):
            print(f"    {i + 1}. {c}")

        # Player B가 먼저 진짜 답 선택
        print(f"\n  [{name_b}] 당신의 진짜 답을 선택하세요 (상대에게 안 보여줘요!)")
        actual = get_choice(len(q.choices))

        # Player A가 예측
        print(f"\n  [{name_a}] {name_b}의 답을 맞춰보세요!")
        predict = get_choice(len(q.choices))

        correct, points = engine.score_predict(predict, actual)
        if correct:
            print(f"\n  정답! +{points}점")
            session.score_a += points
        else:
            print(f"\n  아쉽! {name_b}의 선택: {q.choices[actual]}")

        db.save_couple_answer(session.session_id, name_a, "predict", q.id, str(predict))
        db.save_couple_answer(session.session_id, name_b, "predict_actual", q.id, str(actual))

        # 역할 교대
        print(f"\n  이번엔 반대로!")
        print(f"\n  [{name_a}] 당신의 진짜 답을 선택하세요")
        actual2 = get_choice(len(q.choices))
        print(f"\n  [{name_b}] {name_a}의 답을 맞춰보세요!")
        predict2 = get_choice(len(q.choices))

        correct2, points2 = engine.score_predict(predict2, actual2)
        if correct2:
            print(f"\n  정답! +{points2}점")
            session.score_b += points2
        else:
            print(f"\n  아쉽! {name_a}의 선택: {q.choices[actual2]}")


def _play_balance(engine: CoupleGameEngine, session, name_a: str, name_b: str, db: Database):
    """밸런스 게임"""
    print_header("밸런스 게임 - 우리는 통할까?")
    print("  같은 답을 고르면 싱크로 점수가 올라갑니다!\n")

    questions = engine.get_balance_questions(6)
    answers_a = []
    answers_b = []

    for q in questions:
        print(f"\n  [{q.question}]")
        print(f"    A. {q.option_a}")
        print(f"    B. {q.option_b}")

        print(f"\n  [{name_a}] 선택하세요 (1=A, 2=B)")
        a = "a" if get_choice(2) == 0 else "b"
        answers_a.append(a)

        print(f"  [{name_b}] 선택하세요 (1=A, 2=B)")
        b = "a" if get_choice(2) == 0 else "b"
        answers_b.append(b)

        if a == b:
            session.score_a += 10
            session.score_b += 10
            print("  싱크로! +10점씩!")
        else:
            print("  엇갈림!")

    result = engine.calculate_sync(answers_a, answers_b, questions)
    session.sync_score = result.sync_percentage

    print(f"\n  싱크로율: {result.sync_percentage}% ({result.matched}/{result.total_questions})")
    if result.highlights:
        print(f"\n  일치 항목:")
        for h in result.highlights:
            print(f"    {h}")
    if result.mismatches:
        print(f"\n  엇갈린 항목:")
        for m in result.mismatches:
            print(f"    {m}")


def _play_secret_cards(engine: CoupleGameEngine, session, name_a: str, name_b: str):
    """시크릿 카드"""
    print_header("시크릿 카드 - 마음을 전해보세요")
    print("  상대에게 전하고 싶은 비밀 메시지를 작성하세요.")
    print("  나중에 동시에 공개됩니다!\n")

    cards = engine.get_secret_card_prompts(3)
    messages_a = []
    messages_b = []

    for card in cards:
        print(f"\n  [{card.prompt}]")
        print(f"\n  [{name_a}] 메시지를 적어주세요:")
        msg_a = input("  > ").strip()
        messages_a.append(msg_a)

        print(f"\n  [{name_b}] 메시지를 적어주세요:")
        msg_b = input("  > ").strip()
        messages_b.append(msg_b)

    print_header("시크릿 카드 공개!")
    for i, card in enumerate(cards):
        print(f"\n  [{card.prompt}]")
        print(f"    {name_a}: {messages_a[i]}")
        print(f"    {name_b}: {messages_b[i]}")
        session.score_a += 5
        session.score_b += 5


def _play_challenges(engine: CoupleGameEngine, session):
    """챌린지 미션"""
    print_header("챌린지 미션 - 함께 도전하세요!")
    print("  관계를 더 깊게 만드는 미션들입니다.\n")

    challenges = engine.get_challenge_set(3)
    session.challenges = challenges

    for ch in challenges:
        stars = "★" * ch.difficulty + "☆" * (3 - ch.difficulty)
        print(f"\n  [{ch.title}] 난이도: {stars}  보상: {ch.reward_points}점")
        print(f"    {ch.description}")

    print("\n  미션을 수행하고 다음에 완료 체크하세요!")
    print("  (오늘 바로 할 수 있는 미션부터 시작해보세요)\n")


def main():
    print("\n")
    print("  ╔══════════════════════════════════════╗")
    print("  ║                                      ║")
    print("  ║          I N N E R V I E W            ║")
    print("  ║                                      ║")
    print("  ║   당신을 이해하게 만드는 앱           ║")
    print("  ║                                      ║")
    print("  ╚══════════════════════════════════════╝")
    print("\n  무엇을 하시겠어요?\n")
    print("    1. 나를 찾아 떠나는 여행 (자기이해)")
    print("    2. 커플 게임 (둘이서 함께)")
    print("    3. 종료")

    choice = get_choice(3)

    if choice == 0:
        run_phase1()
    elif choice == 1:
        run_couple_game()
    else:
        print("\n  다음에 또 만나요!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

"""Miromi 웹 데모 - FastAPI + Jinja2 (세션 영속화, 성장 추적)"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.engines.question_engine import QuestionEngine
from lib.engines.scoring_engine import ScoringEngine
from lib.engines.narrative_engine import NarrativeEngine
from lib.engines.couple_game_engine import CoupleGameEngine
from lib.models.user_profile import RelationshipStatus
from lib.db import Database

app = FastAPI(title="Miromi", description="나를 비추는 거울, 당신을 이해하게 만드는 앱")

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

db = Database()

# 인메모리 세션 (DB 백업 있음)
sessions: dict[str, dict] = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/start")
async def start_journey(request: Request):
    """Phase 1 여행 시작 (관계 상태 분기 지원)"""
    data = await request.json() if request.headers.get("content-type") == "application/json" else {}
    rel_status = data.get("relationship_status", "prefer_not_to_say")
    shuffle = data.get("shuffle", False)

    try:
        rs = RelationshipStatus(rel_status)
    except ValueError:
        rs = RelationshipStatus.PREFER_NOT_TO_SAY

    session_id = str(uuid.uuid4())[:8]
    engine = QuestionEngine(phase=1, shuffle=shuffle, relationship_status=rs)
    scoring = ScoringEngine()

    sessions[session_id] = {
        "engine": engine,
        "scoring": scoring,
        "user_id": session_id,
        "relationship_status": rs,
    }

    db.create_user(session_id, "여행자", rel_status)
    db.save_journey_session(session_id, session_id, 0, {}, 1, rel_status)

    q = engine.current_question()
    return {
        "session_id": session_id,
        "question": _format_question(q, engine),
        "progress": {"current": 1, "total": engine.total},
    }


@app.post("/api/answer")
async def answer_question(request: Request):
    """질문에 답변 (세션 영속화)"""
    data = await request.json()
    session_id = data["session_id"]
    choice_index = data["choice_index"]

    session = sessions.get(session_id)
    if not session:
        # DB에서 세션 복구 시도
        saved = db.get_journey_session(session_id)
        if saved and not saved["completed"]:
            rs = RelationshipStatus(saved["relationship_status"])
            engine = QuestionEngine(phase=saved["phase"], relationship_status=rs)
            scoring = ScoringEngine()
            scoring.raw_scores = saved["scoring_data"].get("raw_scores", {})
            scoring.answer_count = saved["scoring_data"].get("answer_count", {})
            engine.current_index = saved["current_index"]
            session = {"engine": engine, "scoring": scoring, "user_id": saved["user_id"],
                       "relationship_status": rs}
            sessions[session_id] = session
        else:
            return JSONResponse({"error": "세션을 찾을 수 없습니다"}, status_code=404)

    engine: QuestionEngine = session["engine"]
    scoring: ScoringEngine = session["scoring"]

    current_q = engine.current_question()
    if current_q:
        db.save_answer(session["user_id"], current_q.id, choice_index, session_id)

    scores = engine.answer(choice_index)
    scoring.add_scores(scores)

    # 세션 DB 저장
    db.save_journey_session(
        session_id, session["user_id"], engine.current_index,
        {"raw_scores": scoring.raw_scores, "answer_count": scoring.answer_count},
        1, session.get("relationship_status", RelationshipStatus.PREFER_NOT_TO_SAY).value,
        completed=engine.is_complete,
    )

    if engine.is_complete:
        rs = session.get("relationship_status", RelationshipStatus.PREFER_NOT_TO_SAY)
        profile = scoring.build_profile(session["user_id"], rs)
        db.save_profile(profile)

        # 성장 추적: 이전 프로파일 비교
        previous = db.get_latest_profile(session["user_id"])
        narrative = NarrativeEngine()
        report = narrative.generate_report(profile, previous if previous and previous.user_id == profile.user_id else None)

        return {
            "complete": True,
            "report": _format_report(report),
            "scores": {
                "big_five": profile.big_five.model_dump(),
                "attachment": {
                    **profile.attachment.model_dump(),
                    "dominant_type": profile.attachment.dominant_type,
                    "blend": profile.attachment.blend_description,
                    "is_mixed": profile.attachment.is_mixed,
                    "spectrum": profile.attachment.spectrum,
                },
                "love_triangle": {
                    **profile.love_triangle.model_dump(),
                    "love_type": profile.love_triangle.love_type,
                    "strongest": profile.love_triangle.strongest,
                    "weakest": profile.love_triangle.weakest,
                },
            },
            "confidences": scoring.get_all_confidences(),
        }

    q = engine.current_question()
    return {
        "complete": False,
        "question": _format_question(q, engine),
        "progress": {"current": engine.current_index + 1, "total": engine.total},
    }


@app.post("/api/couple/start")
async def start_couple_game():
    """커플 게임 시작"""
    game_engine = CoupleGameEngine()
    session_id = str(uuid.uuid4())[:8]

    balance_qs = game_engine.get_balance_questions(8)
    predict_qs = game_engine.get_predict_questions(4)

    sessions[f"couple_{session_id}"] = {
        "engine": game_engine,
        "balance_qs": balance_qs,
        "predict_qs": predict_qs,
    }

    return {
        "session_id": session_id,
        "balance_questions": [
            {"id": q.id, "question": q.question, "option_a": q.option_a, "option_b": q.option_b}
            for q in balance_qs
        ],
        "predict_questions": [
            {"id": q.id, "situation": q.situation, "question": q.question, "choices": q.choices}
            for q in predict_qs
        ],
    }


@app.post("/api/couple/balance")
async def couple_balance(request: Request):
    """밸런스 게임 결과"""
    data = await request.json()
    session_id = data["session_id"]
    answers_a = data["answers_a"]
    answers_b = data["answers_b"]

    session = sessions.get(f"couple_{session_id}")
    if not session:
        return JSONResponse({"error": "세션을 찾을 수 없습니다"}, status_code=404)

    engine: CoupleGameEngine = session["engine"]
    result = engine.calculate_sync(answers_a, answers_b, session["balance_qs"])

    return {
        "sync_percentage": result.sync_percentage,
        "matched": result.matched,
        "total": result.total_questions,
        "highlights": result.highlights,
        "mismatches": result.mismatches,
    }


@app.post("/api/couple/predict")
async def couple_predict(request: Request):
    """예측 게임 결과"""
    data = await request.json()
    prediction = data["prediction"]
    actual = data["actual"]

    correct = prediction == actual
    points = 15 if correct else 0

    return {"correct": correct, "points": points}


@app.get("/api/challenges")
async def get_challenges():
    """챌린지 미션 목록"""
    engine = CoupleGameEngine()
    challenges = engine.get_challenge_set(3)
    return [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "difficulty": c.difficulty,
            "reward_points": c.reward_points,
        }
        for c in challenges
    ]


def _format_question(q, engine: QuestionEngine = None) -> dict:
    if q is None:
        return {}
    result = {
        "id": q.id,
        "category": q.category.value,
        "narrative": q.narrative,
        "question": q.question,
        "choices": [{"text": c.text} for c in q.choices],
    }
    if engine:
        result["phase_intro"] = engine.get_phase_intro()
    return result


def _format_report(report) -> dict:
    return {
        "profile_summary": report.profile_summary,
        "struggle_reason": report.struggle_reason,
        "comfort_message": report.comfort_message,
        "sections": [
            {
                "title": s.title,
                "summary": s.summary,
                "icon": s.icon,
                "color": s.color,
                "insights": [
                    {
                        "title": i.title,
                        "description": i.description,
                        "empathy_message": i.empathy_message,
                        "priority": i.priority.value,
                        "color_hint": i.color_hint,
                    }
                    for i in s.insights
                ],
            }
            for s in report.sections
        ],
        "action_tips": report.action_tips,
        "action_plan": [
            {"week": s.week, "action": s.action, "reason": s.reason}
            for s in report.action_plan
        ],
        "tension_insights": [
            {
                "title": t.title,
                "description": t.description,
                "empathy_message": t.empathy_message,
                "color_hint": t.color_hint,
            }
            for t in report.tension_insights
        ],
        "growth_notes": report.growth_notes,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

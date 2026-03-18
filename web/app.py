"""Miromi 웹 데모 - FastAPI + Jinja2"""

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
from lib.db import Database

app = FastAPI(title="Miromi", description="나를 비추는 거울, 당신을 이해하게 만드는 앱")

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

db = Database()

# 세션 저장 (간단한 인메모리)
sessions: dict[str, dict] = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/start")
async def start_journey():
    """Phase 1 여행 시작"""
    session_id = str(uuid.uuid4())[:8]
    engine = QuestionEngine(phase=1)
    scoring = ScoringEngine()

    sessions[session_id] = {
        "engine": engine,
        "scoring": scoring,
        "user_id": session_id,
    }
    db.create_user(session_id, "여행자")

    q = engine.current_question()
    return {
        "session_id": session_id,
        "question": _format_question(q),
        "progress": {"current": 1, "total": engine.total},
    }


@app.post("/api/answer")
async def answer_question(request: Request):
    """질문에 답변"""
    data = await request.json()
    session_id = data["session_id"]
    choice_index = data["choice_index"]

    session = sessions.get(session_id)
    if not session:
        return JSONResponse({"error": "세션을 찾을 수 없습니다"}, status_code=404)

    engine: QuestionEngine = session["engine"]
    scoring: ScoringEngine = session["scoring"]

    current_q = engine.current_question()
    if current_q:
        db.save_answer(session["user_id"], current_q.id, choice_index)

    scores = engine.answer(choice_index)
    scoring.add_scores(scores)

    if engine.is_complete:
        profile = scoring.build_profile(session["user_id"])
        db.save_profile(profile)
        narrative = NarrativeEngine()
        report = narrative.generate_report(profile)

        return {
            "complete": True,
            "report": {
                "profile_summary": report.profile_summary,
                "struggle_reason": report.struggle_reason,
                "comfort_message": report.comfort_message,
                "sections": [
                    {
                        "title": s.title,
                        "summary": s.summary,
                        "insights": [
                            {
                                "title": i.title,
                                "description": i.description,
                                "empathy_message": i.empathy_message,
                            }
                            for i in s.insights
                        ],
                    }
                    for s in report.sections
                ],
                "action_tips": report.action_tips,
            },
            "scores": {
                "big_five": profile.big_five.model_dump(),
                "attachment": profile.attachment.model_dump(),
                "love_triangle": profile.love_triangle.model_dump(),
            },
        }

    q = engine.current_question()
    return {
        "complete": False,
        "question": _format_question(q),
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
        "balance_answers_a": [],
        "balance_answers_b": [],
        "predict_index": 0,
        "score_a": 0,
        "score_b": 0,
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


def _format_question(q) -> dict:
    if q is None:
        return {}
    return {
        "id": q.id,
        "category": q.category.value,
        "narrative": q.narrative,
        "question": q.question,
        "choices": [{"text": c.text} for c in q.choices],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

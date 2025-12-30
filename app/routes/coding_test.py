from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.coding_test import CodingTest
from app.models.coding_question import CodingQuestion
from flask_login import login_required, current_user
from app.extensions import db
from app.models.coding_test_progress import CodingTestProgress
from app.ml.analyzer import analyze_test


coding_test_bp = Blueprint(
    "coding_test",
    __name__,
    url_prefix="/coding-tests"
)

@coding_test_bp.route("/")
@login_required
def list_tests():
    tests = CodingTest.query.all()
    return render_template("coding_tests/list.html", tests=tests)

@coding_test_bp.route("/<int:test_id>/solve/<int:index>")
@login_required
def solve_question(test_id, index):
    test = CodingTest.query.get_or_404(test_id)
    questions = test.questions

    if index < 0 or index >= len(questions):
        return "Invalid question index", 404

    question = questions[index]

    return render_template(
        "coding_tests/solve.html",
        test=test,
        question=question,
        index=index,
        total=len(questions)
    )

@coding_test_bp.route("/<int:test_id>")
@login_required
def test_overview(test_id):
    test = CodingTest.query.get_or_404(test_id)
    return render_template("coding_tests/overview.html", test=test)

@coding_test_bp.route("/submit-result", methods=["POST"])
@login_required
def submit_result():
    data = request.get_json()

    test_id = int(data["test_id"])
    question_id = int(data["question_id"])
    status = data["status"]
    time_taken = int(data.get("time_taken", 0))

    question = CodingQuestion.query.get_or_404(question_id)

    difficulty = (question.difficulty or "").strip().lower()

    XP_MAP = {
        "easy": 10,
        "medium": 20,
        "hard": 30
    }


    progress = CodingTestProgress.query.filter_by(
        user_id=current_user.id,
        test_id=test_id,
        question_id=question_id
    ).first()

    if not progress:
        progress = CodingTestProgress(
            user_id=current_user.id,
            test_id=test_id,
            question_id=question_id
        )
        db.session.add(progress)

    progress.status = status
    progress.time_taken = time_taken

    # 🏆 XP ONLY ONCE & ONLY IF PASSED
    if status == "Passed" and not progress.xp_awarded:
        xp = XP_MAP.get(difficulty, 0)
        current_user.xp += xp
        progress.xp_awarded = True

    db.session.commit()

    return jsonify({"ok": True})

@coding_test_bp.route("/<int:test_id>/result")
@login_required
def result(test_id):
    test = CodingTest.query.get_or_404(test_id)

    # ---------------- FETCH PROGRESS ----------------
    progresses = CodingTestProgress.query.filter_by(
        user_id=current_user.id,
        test_id=test_id
    ).all()

    # Map question_id -> progress
    progress_map = {p.question_id: p for p in progresses}

    # ---------------- XP / TABLE LOGIC ----------------
    XP_MAP = {
        "easy": 10,
        "medium": 20,
        "hard": 30
    }

    table = []
    passed = 0
    total_time = 0
    xp_earned = 0

    for q in test.questions:
        difficulty = (q.difficulty or "").strip().lower()
        p = progress_map.get(q.id)

        if p:
            status = p.status
            time_taken = p.time_taken or 0
            total_time += time_taken

            if status == "Passed":
                passed += 1

            if p.xp_awarded:
                xp_earned += XP_MAP.get(difficulty, 0)
        else:
            status = "Not Attempted"
            time_taken = 0

        table.append({
            "title": q.title,
            "difficulty": difficulty,
            "status": status,
            "time_taken": time_taken
        })

    # ---------------- ML ANALYSIS ----------------
    analysis_data = analyze_test(test, progress_map)

    # ---------------- GEMINI EXPLANATIONS ----------------
    # Import here to avoid circular imports
    from app.utils.topic_explainer import explain_topic

    topic_explanations = {}

    for topic, details in analysis_data["details"].items():
        try:
            explanation = explain_topic(
                topic=topic,
                level=details["level"],
                stats=details
            )
        except Exception as e:
            # Fallback (never break result page)
            explanation = (
                f"You are currently at {details['level']} level in {topic}. "
                f"Practice more questions to improve consistency and confidence."
            )

        topic_explanations[topic] = explanation

    # ---------------- RENDER RESULT ----------------
    return render_template(
        "coding_tests/result.html",
        test=test,
        results=table,
        passed=passed,
        total=len(test.questions),
        total_time=total_time,
        xp_earned=xp_earned,
        analysis=analysis_data,
        explanations=topic_explanations
    )

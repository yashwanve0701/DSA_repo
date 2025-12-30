from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.coding_question import CodingQuestion
import requests
import json

coding_bp = Blueprint("coding", __name__, url_prefix="/coding")

PISTON_URL = "https://emkc.org/api/v2/piston/execute"

LANGUAGE_CONFIG = {
    "python": {"language": "python", "version": "3.10.0"},
    "cpp": {"language": "cpp", "version": "10.2.0"},
    "java": {"language": "java", "version": "15.0.2"}
}

# -----------------------------------------------
# Show all coding questions
# -----------------------------------------------
@coding_bp.route("/")
@login_required
def all_questions():
    questions = CodingQuestion.query.all()
    return render_template("coding/all_questions.html", questions=questions)

# -----------------------------------------------
# Show a specific coding question
# -----------------------------------------------
@coding_bp.route("/<int:id>")
@login_required
def coding_page(id):
    question = CodingQuestion.query.get_or_404(id)
    return render_template("coding/practice.html", question=question)

# -----------------------------------------------
# Run Code (Sample Input)
# -----------------------------------------------
@coding_bp.route("/run", methods=["POST"])
@login_required
def run_code():
    data = request.get_json()
    language = data.get("language")
    code = data.get("code")
    stdin = data.get("stdin", "")

    if language not in LANGUAGE_CONFIG:
        return jsonify({"error": "Unsupported language"}), 400

    payload = {
        "language": LANGUAGE_CONFIG[language]["language"],
        "version": LANGUAGE_CONFIG[language]["version"],
        "files": [{"name": f"main.{language}", "content": code}],
        "stdin": stdin
    }

    try:
        res = requests.post(PISTON_URL, json=payload, timeout=10)
        result = res.json()
        output = result["run"]["output"]
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------
# Submit Code (Hidden Test Cases)
# -----------------------------------------------

from app.utils.complexity_analyzer import analyze_time_complexity
import json

@coding_bp.route("/submit", methods=["POST"])
@login_required
def submit_code():
    data = request.get_json()
    language = data.get("language")
    code = data.get("code")
    qid = data.get("question_id")

    question = CodingQuestion.query.get(qid)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    test_cases = json.loads(question.test_cases)
    results = []
    passed = 0

    for case in test_cases:
        stdin = case["input"]
        expected_output = case["output"].strip()

        payload = {
            "language": LANGUAGE_CONFIG[language]["language"],
            "version": LANGUAGE_CONFIG[language]["version"],
            "files": [{"name": f"main.{language}", "content": code}],
            "stdin": stdin
        }

        try:
            res = requests.post(PISTON_URL, json=payload, timeout=10)
            result = res.json()
            output = result["run"]["output"].strip()

            if output == expected_output:
                passed += 1
                results.append({"input": stdin, "output": output, "status": "Passed"})
            else:
                results.append({
                    "input": stdin,
                    "output": output,
                    "expected": expected_output,
                    "status": "Failed"
                })
        except Exception as e:
            results.append({"input": stdin, "output": str(e), "status": "Error"})

    # 🔥 CALL GEMINI ONLY ONCE
    complexity = analyze_time_complexity(
        code=code,
        problem=question.description,
        language=language
    )

    # ✅ Store analysis in session (TEMP)
    from flask import session
    session["last_complexity_analysis"] = complexity
    session["last_question_id"] = qid

    return jsonify({
        "passed": passed,
        "total": len(test_cases),
        "results": results,
        "analysis_ready": True
    })

from flask import session

@coding_bp.route("/analysis/<int:question_id>")
@login_required
def view_analysis(question_id):
    analysis = session.get("last_complexity_analysis")
    qid = session.get("last_question_id")

    if not analysis or qid != question_id:
        return "No analysis found. Please submit code first.", 400

    question = CodingQuestion.query.get_or_404(question_id)

    return render_template(
        "coding/analysis.html",
        question=question,
        analysis=analysis
    )

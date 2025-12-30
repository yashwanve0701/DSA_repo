from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models.coding_question import CodingQuestion
import json

admin_coding_bp = Blueprint("admin_coding", __name__, url_prefix="/admin/coding")

# Check admin login
def admin_logged_in():
    return session.get("admin_logged_in")

# --------------------------------------------------
# Show all coding questions
# --------------------------------------------------
@admin_coding_bp.route("/")
def dashboard():
    if not admin_logged_in():
        return redirect(url_for("admin.admin_login"))
    questions = CodingQuestion.query.all()
    return render_template("admin/coding_dashboard.html", questions=questions)

# --------------------------------------------------
# Add new coding question
# --------------------------------------------------
@admin_coding_bp.route("/add", methods=["GET", "POST"])
def add_question():
    if not admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        sample_input = request.form.get("sample_input")
        sample_output = request.form.get("sample_output")
        difficulty = request.form.get("difficulty")
        test_cases = request.form.get("test_cases")

        # Validate JSON format for test cases
        try:
            json.loads(test_cases)
        except Exception as e:
            flash("❌ Invalid JSON format in test cases!", "danger")
            return redirect(url_for("admin_coding.add_question"))

        new_q = CodingQuestion(
            title=title,
            description=description,
            sample_input=sample_input,
            sample_output=sample_output,
            difficulty=difficulty,
            test_cases=test_cases
        )
        db.session.add(new_q)
        db.session.commit()
        flash("✅ Coding question added successfully!", "success")
        return redirect(url_for("admin_coding.dashboard"))

    return render_template("admin/add_coding.html")

# --------------------------------------------------
# Delete question
# --------------------------------------------------
@admin_coding_bp.route("/delete/<int:id>")
def delete_question(id):
    if not admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    q = CodingQuestion.query.get_or_404(id)
    db.session.delete(q)
    db.session.commit()
    flash("🗑️ Question deleted.", "info")
    return redirect(url_for("admin_coding.dashboard"))

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.extensions import db
from app.models.coding_test import CodingTest
from app.models.topic import Topic
from app.models.coding_question import CodingQuestion

admin_coding_test_bp = Blueprint(
    "admin_coding_test",
    __name__,
    url_prefix="/admin/coding-tests"
)

def admin_logged_in():
    return session.get("admin_logged_in")


@admin_coding_test_bp.route("/")
def dashboard():
    if not admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    tests = CodingTest.query.all()
    return render_template("admin/coding_test_dashboard.html", tests=tests)


@admin_coding_test_bp.route("/create", methods=["GET", "POST"])
def create_test():
    if not admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    topics = Topic.query.all()
    questions = CodingQuestion.query.all()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        topic_ids = request.form.getlist("topics")
        question_ids = request.form.getlist("questions")

        test = CodingTest(title=title, description=description)

        for tid in topic_ids:
            test.topics.append(Topic.query.get(int(tid)))

        for qid in question_ids:
            test.questions.append(CodingQuestion.query.get(int(qid)))

        db.session.add(test)
        db.session.commit()

        flash("✅ Coding Test created", "success")
        return redirect(url_for("admin_coding_test.dashboard"))

    return render_template(
        "admin/create_coding_test.html",
        topics=topics,
        questions=questions
    )

@admin_coding_test_bp.route("/<int:test_id>/delete", methods=["POST"])
def delete_test(test_id):
    if not admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    test = CodingTest.query.get_or_404(test_id)

    # Remove relationships first (important)
    test.topics.clear()
    test.questions.clear()

    db.session.delete(test)
    db.session.commit()

    flash("🗑 Coding test deleted successfully", "success")
    return redirect(url_for("admin_coding_test.dashboard"))

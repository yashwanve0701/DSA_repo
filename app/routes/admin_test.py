from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.extensions import db
from app.models.test import Test
from app.models.topic import Topic
from app.models.test_question import TestQuestion

admin_test_bp = Blueprint(
    "admin_test",
    __name__,
    url_prefix="/admin/tests"
)

def admin_logged_in():
    return session.get("admin_logged_in")


@admin_test_bp.route("/")
def dashboard():
    if not admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    tests = Test.query.all()
    return render_template("admin/test_dashboard.html", tests=tests)

@admin_test_bp.route("/create", methods=["GET", "POST"])
def create_test():
    if not admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    topics = Topic.query.all()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        topic_ids = request.form.getlist("topics")

        test = Test(title=title, description=description)

        for tid in topic_ids:
            topic = Topic.query.get(int(tid))
            test.topics.append(topic)

        db.session.add(test)
        db.session.commit()

        flash("✅ Test created successfully", "success")
        return redirect(url_for("admin_test.add_question", test_id=test.id))

    return render_template("admin/create_test.html", topics=topics)


@admin_test_bp.route("/<int:test_id>/add-question", methods=["GET", "POST"])
def add_question(test_id):
    if not admin_logged_in():
        return redirect(url_for("admin.admin_login"))

    test = Test.query.get_or_404(test_id)

    if request.method == "POST":
        q = TestQuestion(
            test_id=test.id,
            question=request.form.get("question"),
            option_a=request.form.get("option_a"),
            option_b=request.form.get("option_b"),
            option_c=request.form.get("option_c"),
            option_d=request.form.get("option_d"),
            correct_option=request.form.get("correct_option"),
        )

        db.session.add(q)
        db.session.commit()

        flash("➕ Question added", "success")
        return redirect(url_for("admin_test.add_question", test_id=test.id))

    return render_template(
        "admin/add_test_question.html",
        test=test,
        questions=test.questions
    )



from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.extensions import db
from app.models.topic import Topic
from app.models.user import User
from app.models.topic import Topic
from app.models.coding_question import CodingQuestion
from app.models.badge import Badge, UserBadge
from app.models.coding_test import CodingTest   # adjust import if needed
from sqlalchemy import func

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ---------------------------
# Admin Login
# ---------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Welcome, Admin!", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("admin.admin_login"))

    return render_template("admin/login.html")


# ---------------------------
# Admin Dashboard
# ---------------------------
@admin_bp.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    # 🔢 TOTAL COUNTS
    total_users = User.query.count()
    total_topics = Topic.query.count()
    total_coding_questions = CodingQuestion.query.count()
    total_coding_tests = CodingTest.query.count()
    total_badges = Badge.query.count()

    # 🏅 BADGE → USER COUNT
    badge_stats = (
        db.session.query(
            Badge.name,
            Badge.icon,
            Badge.color,
            func.count(UserBadge.user_id).label("user_count")
        )
        .outerjoin(UserBadge, Badge.id == UserBadge.badge_id)
        .group_by(Badge.id)
        .order_by(Badge.xp_threshold.asc())
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_topics=total_topics,
        total_coding_questions=total_coding_questions,
        total_coding_tests=total_coding_tests,
        total_badges=total_badges,
        badge_stats=badge_stats
    )

# ---------------------------
# Add Topic
# ---------------------------
@admin_bp.route("/add_topic", methods=["GET", "POST"])
def add_topic():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":
        title = request.form.get("title")
        intro = request.form.get("intro")
        example = request.form.get("example")
        code = request.form.get("code")
        details = request.form.get("details")
        tags = request.form.get("tags")

        # ✅ Combine all sections into one HTML-formatted description
        description = f"""
        <section>
            <h4>Introduction</h4>
            <p>{intro}</p>
        </section>
        <section>
            <h4>Example / Explanation</h4>
            <p>{example}</p>
        </section>
        <section>
            <h4>Code Example</h4>
            <pre><code>{code}</code></pre>
        </section>
        <section>
            <h4>Additional Details</h4>
            <p>{details}</p>
        </section>
        """

        new_topic = Topic(title=title, description=description, tags=tags)
        db.session.add(new_topic)
        db.session.commit()

        flash("Topic added successfully!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/add_topic.html")

# ---------------------------
# Delete Topic
# ---------------------------
@admin_bp.route("/delete/<int:id>")
def delete_topic(id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    topic = Topic.query.get_or_404(id)
    db.session.delete(topic)
    db.session.commit()
    flash("Topic deleted successfully!", "info")
    return redirect(url_for("admin.dashboard"))


# ---------------------------
# Logout
# ---------------------------
@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("admin.admin_login"))


# ---------------------------
# View All Topics
# ---------------------------
@admin_bp.route("/topics")
def all_topics():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.admin_login"))

    topics = Topic.query.all()
    return render_template("admin/all_topics.html", topics=topics)

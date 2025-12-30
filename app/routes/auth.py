from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.user import User
from app.models.topic import UserTopicProgress
from app.models.topic import Topic
from app.models.badge import Badge,UserBadge
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# --------------------------
# Signup
# --------------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for("auth.signup"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html")


# --------------------------
# Login
# --------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


# --------------------------
# Dashboard (for testing)
# --------------------------
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    from app.routes.badge import init_badges
    from app.models.topic import Topic, UserTopicProgress
    from app.models.badge import Badge, UserBadge
    # 1️⃣ Initialize badges (idempotent)
    init_badges()

    # 2️⃣ Award badges based on XP
    current_user.check_and_award_badges()

    # 3️⃣ User XP (always int)
    xp = int(current_user.xp or 0)

    # 4️⃣ Topic progress stats
    total_topics = Topic.query.count()

    progresses = UserTopicProgress.query.filter_by(
        user_id=current_user.id
    ).all()

    completed_count = sum(1 for p in progresses if p.completed)
    bookmarked_count = sum(1 for p in progresses if p.bookmarked)
    total_time = sum(p.total_time_spent or 0 for p in progresses)

    progress_percent = int((completed_count / total_topics) * 100) if total_topics else 0

    # 5️⃣ Badges
    all_badges = Badge.query.order_by(Badge.xp_threshold.asc()).all()

    earned_badge_ids = [
        ub.badge_id
        for ub in UserBadge.query.filter_by(user_id=current_user.id).all()
    ]

    # 6️⃣ Equipped badge
    equipped_badge = None
    if current_user.equipped_badge_id:
        equipped_badge = Badge.query.get(current_user.equipped_badge_id)

    # 7️⃣ Next badge
    next_badge = None
    for badge in all_badges:
        if badge.id not in earned_badge_ids:
            next_badge = badge
            break

    # 8️⃣ Current badge (highest earned)
    current_badge = None
    if earned_badge_ids:
        current_badge = (
            Badge.query
            .filter(Badge.id.in_(earned_badge_ids))
            .order_by(Badge.xp_threshold.desc())
            .first()
        )

    # 9️⃣ Next badge progress (🔥 FIX)
    next_badge_progress_percent = 0
    xp_needed_for_next = 0

    if next_badge:
        xp_needed_for_next = max(next_badge.xp_threshold - xp, 0)
        if next_badge.xp_threshold > 0:
            next_badge_progress_percent = min(
                int((xp / next_badge.xp_threshold) * 100),
                100
            )
        else:
            next_badge_progress_percent = 100

    return render_template(
        "auth/dashboard.html",
        xp=xp,
        completed_count=completed_count,
        bookmarked_count=bookmarked_count,
        total_time=total_time,
        progress_percent=progress_percent,
        all_badges=all_badges,
        earned_badge_ids=earned_badge_ids,
        next_badge=next_badge,
        next_badge_progress_percent=next_badge_progress_percent,
        xp_needed_for_next=xp_needed_for_next,
        equipped_badge=equipped_badge,
        current_badge=current_badge,
    )

# --------------------------
# Logout
# --------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))





from flask import Blueprint, render_template, request,flash,redirect,url_for
from flask_login import login_required
from app.models.topic import Topic
from app.utils.youtube_api import get_videos
from app.models.topic import UserTopicProgress
from datetime import datetime
from flask_login import current_user  
from app.extensions import db
from app.utils.gemini_quiz import generate_mcq_quiz
import json


study_bp = Blueprint("study", __name__, url_prefix="/study")


# --------------------------
# Show All Topics
# --------------------------
from app.models.topic import UserTopicProgress
from flask_login import current_user

@study_bp.route("/")
@login_required
def all_topics():
    search_query = request.args.get("search")

    if search_query:
        topics = Topic.query.filter(
            Topic.title.ilike(f"%{search_query}%")
        ).all()
    else:
        topics = Topic.query.all()

    # Fetch all progress rows for current user
    progresses = UserTopicProgress.query.filter_by(
        user_id=current_user.id
    ).all()

    completed_topic_ids = set()
    revision_map = {}
    time_spent_map = {}

    for p in progresses:
        if p.completed:
            completed_topic_ids.add(p.topic_id)

        revision_map[p.topic_id] = p.revision_count
        time_spent_map[p.topic_id] = p.total_time_spent
    
    bookmark_map = {p.topic_id: p.bookmarked for p in progresses}

    return render_template(
        "study/topics.html",
        topics=topics,
        completed_topic_ids=completed_topic_ids,
        revision_map=revision_map,
        time_spent_map=time_spent_map,
        search_query=search_query,
        xp=current_user.xp,
        bookmark_map=bookmark_map
    )

# --------------------------
# Topic Detail Page
# --------------------------


@study_bp.route("/<int:topic_id>")
@login_required
def topic_detail(topic_id):
    topic = Topic.query.get_or_404(topic_id)

    progress = UserTopicProgress.query.filter_by(
        user_id=current_user.id,
        topic_id=topic_id
    ).first()

    if not progress:
        progress = UserTopicProgress(
            user_id=current_user.id,
            topic_id=topic_id,
            revision_count=1,
            total_time_spent=0
        )
        db.session.add(progress)
    else:
        progress.revision_count += 1

    progress.last_accessed_at = datetime.utcnow()
    db.session.commit()

    videos = get_videos(topic.title)

    return render_template(
        "study/topic_detail.html",
        topic=topic,
        videos=videos,
        is_completed=progress.completed,
        revision_count=progress.revision_count,
        time_spent=progress.total_time_spent or 0  # ✅ ALWAYS defined
    )



@study_bp.route("/<int:topic_id>/complete", methods=["POST"])
@login_required
def complete_topic(topic_id):
    # Check if progress already exists
    progress = UserTopicProgress.query.filter_by(
        user_id=current_user.id,
        topic_id=topic_id
    ).first()

    if progress and progress.completed:
        flash("Topic already completed.", "info")
        return redirect(url_for("study.topic_detail", topic_id=topic_id))

    if not progress:
        progress = UserTopicProgress(
            user_id=current_user.id,
            topic_id=topic_id
        )
        db.session.add(progress)

    # Mark completed
    progress.completed = True
    progress.completed_at = datetime.utcnow()

    # Add XP
    current_user.xp += 10
    current_user.check_and_award_badges()

    db.session.commit()

    flash("🎉 Topic completed! +10 XP earned.", "success")
    return redirect(url_for("study.topic_detail", topic_id=topic_id))



import json

@study_bp.route("/<int:topic_id>/track-time", methods=["POST"])
@login_required
def track_time(topic_id):
    try:
        data = request.get_json(silent=True) or {}
        seconds = int(data.get("seconds", 0))
    except Exception:
        return "", 204

    if seconds <= 0:
        return "", 204

    progress = UserTopicProgress.query.filter_by(
        user_id=current_user.id,
        topic_id=topic_id
    ).first()

    if progress:
        progress.total_time_spent += seconds
        db.session.commit()

    return "", 204

from flask import session
@study_bp.route("/<int:topic_id>/quiz")
@login_required
def topic_quiz(topic_id):
    topic = Topic.query.get_or_404(topic_id)

    progress = UserTopicProgress.query.filter_by(
        user_id=current_user.id,
        topic_id=topic_id
    ).first()

    quiz = generate_mcq_quiz(topic.title)

    # 🔐 Store quiz securely in session
    session[f"quiz_{topic_id}"] = quiz

    return render_template(
        "study/topic_quiz.html",
        topic=topic,
        quiz=quiz
    )

@study_bp.route("/<int:topic_id>/quiz/submit", methods=["POST"])
@login_required
def submit_quiz(topic_id):
    topic = Topic.query.get_or_404(topic_id)

    quiz = session.get(f"quiz_{topic_id}")
    if not quiz:
        return redirect(url_for("study.topic_quiz", topic_id=topic_id))

    score = 0
    results = []

    for i, q in enumerate(quiz):
        user_answer = request.form.get(f"q{i}")
        user_answer = int(user_answer) if user_answer is not None else None

        correct_index = q["correct_index"]
        is_correct = user_answer == correct_index

        if is_correct:
            score += 1

        results.append({
            "question": q["question"],
            "options": q["options"],
            "correct_index": correct_index,
            "user_answer": user_answer,
            "is_correct": is_correct
        })

    passed_now = score >= 3

    # Fetch or create progress
    progress = UserTopicProgress.query.filter_by(
        user_id=current_user.id,
        topic_id=topic_id
    ).first()

    if not progress:
        progress = UserTopicProgress(
            user_id=current_user.id,
            topic_id=topic_id
        )
        db.session.add(progress)

    already_passed = progress.quiz_passed  # IMPORTANT

    # ✅ Only upgrade state (never downgrade)
    if passed_now and not progress.quiz_passed:
        progress.quiz_passed = True
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        current_user.xp = (current_user.xp or 0) + 10

    db.session.commit()

    # Render SAME page with results (no redirect)
    return render_template(
        "study/topic_quiz.html",
        topic=topic,
        quiz=quiz,
        results=results,
        score=score,
        passed=passed_now,
        already_passed=already_passed
    )


@study_bp.route("/<int:topic_id>/bookmark", methods=["POST"])
@login_required
def toggle_bookmark(topic_id):
    progress = UserTopicProgress.query.filter_by(
        user_id=current_user.id,
        topic_id=topic_id
    ).first()

    if not progress:
        progress = UserTopicProgress(
            user_id=current_user.id,
            topic_id=topic_id
        )
        db.session.add(progress)

    progress.bookmarked = not progress.bookmarked
    db.session.commit()

    return redirect(url_for("study.all_topics"))

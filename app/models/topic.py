from app.extensions import db

class Topic(db.Model):
    __tablename__ = "topics"   # ✅ ADD THIS

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(100))

from app.extensions import db
from datetime import datetime

class UserTopicProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)

    # Completion
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    # 🔁 Revision tracking
    revision_count = db.Column(db.Integer, default=0, nullable=False)

    # ⏱ Time tracking (seconds)
    total_time_spent = db.Column(db.Integer, default=0, nullable=False)

    # ⭐ Bookmarking
    bookmarked = db.Column(db.Boolean, default=False)

    # 🧠 Quiz gate
    quiz_passed = db.Column(db.Boolean, default=False)

    # Analytics
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "topic_id", name="unique_user_topic"),
    )

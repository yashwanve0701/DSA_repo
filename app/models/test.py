from app.extensions import db
from datetime import datetime
from app.models.test_topic import test_topics   # 🔴 REQUIRED

class Test(db.Model):
    __tablename__ = "tests"   # ✅ ADD THIS

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    topics = db.relationship(
        "Topic",
        secondary=test_topics,   # 🔴 USE VARIABLE, NOT STRING
        backref="tests"
    )

    questions = db.relationship(
        "TestQuestion",
        backref="test",
        cascade="all, delete-orphan"
    )
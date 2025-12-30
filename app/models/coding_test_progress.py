from app.extensions import db
from datetime import datetime

class CodingTestProgress(db.Model):
    __tablename__ = "coding_test_progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    test_id = db.Column(
        db.Integer,
        db.ForeignKey("coding_tests.id"),
        nullable=False,
        index=True
    )

    question_id = db.Column(
        db.Integer,
        db.ForeignKey("coding_questions.id"),
        nullable=False
    )

    status = db.Column(db.String(20))
    time_taken = db.Column(db.Integer)
    xp_awarded = db.Column(db.Boolean, default=False)

    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "test_id", "question_id",
            name="uq_user_test_question"
        ),
    )

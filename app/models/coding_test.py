from app.extensions import db
from datetime import datetime
from app.models.coding_test_topic import coding_test_topics
from app.models.coding_test_question import coding_test_questions

from app.extensions import db
from datetime import datetime

class CodingTest(db.Model):
    __tablename__ = "coding_tests"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    topics = db.relationship(
        "Topic",
        secondary="coding_test_topics",
        backref="coding_tests"
    )

    questions = db.relationship(
        "CodingQuestion",
        secondary="coding_test_questions",
        backref="coding_tests"
    )

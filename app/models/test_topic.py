from app.extensions import db

test_topics = db.Table(
    "test_topics",
    db.Column("test_id", db.Integer, db.ForeignKey("tests.id"), primary_key=True),
    db.Column("topic_id", db.Integer, db.ForeignKey("topics.id"), primary_key=True),
)

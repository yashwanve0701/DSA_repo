from app.extensions import db

coding_test_topics = db.Table(
    "coding_test_topics",
    db.Column(
        "coding_test_id",
        db.Integer,
        db.ForeignKey("coding_tests.id"),
        primary_key=True
    ),
    db.Column(
        "topic_id",
        db.Integer,
        db.ForeignKey("topics.id"),
        primary_key=True
    ),
)

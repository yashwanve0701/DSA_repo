from app.extensions import db

coding_test_questions = db.Table(
    "coding_test_questions",
    db.Column(
        "coding_test_id",
        db.Integer,
        db.ForeignKey("coding_tests.id"),
        primary_key=True
    ),
    db.Column(
        "coding_question_id",
        db.Integer,
        db.ForeignKey("coding_questions.id"),
        primary_key=True
    ),
)

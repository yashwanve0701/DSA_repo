from app.extensions import db

class TestQuestion(db.Model):
    __tablename__ = "test_questions"   # ✅ strongly recommended

    id = db.Column(db.Integer, primary_key=True)

    test_id = db.Column(
        db.Integer,
        db.ForeignKey("tests.id"),
        nullable=False
    )

    question = db.Column(db.Text, nullable=False)

    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)

    correct_option = db.Column(db.String(1), nullable=False)  # A / B / C / D

from app.extensions import db

class CodingQuestion(db.Model):
    __tablename__ = "coding_questions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    sample_input = db.Column(db.Text, nullable=True)
    sample_output = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(50), nullable=True)
    test_cases = db.Column(db.Text, nullable=True)

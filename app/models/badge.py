from app.extensions import db
from datetime import datetime

class Badge(db.Model):
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(20), nullable=False)
    xp_threshold = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ Relationship
    users = db.relationship(
        "UserBadge",
        back_populates="badge",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Badge {self.name}>"

class UserBadge(db.Model):
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )

    badge_id = db.Column(
        db.Integer,
        db.ForeignKey('badges.id', ondelete="CASCADE"),
        nullable=False
    )

    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),
    )

    # ✅ Relationships
    user = db.relationship("User", back_populates="badges")
    badge = db.relationship("Badge", back_populates="users")

    def __repr__(self):
        return f"<UserBadge user={self.user_id} badge={self.badge_id}>"

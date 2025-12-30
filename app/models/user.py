# user.py
from app.extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from datetime import datetime

from app.extensions import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    xp = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ FIX: Proper ForeignKey
    equipped_badge_id = db.Column(
        db.Integer,
        db.ForeignKey('badges.id'),
        nullable=True
    )

    # ✅ FIX: Relationship
    badges = db.relationship(
        "UserBadge",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Optional relationship to equipped badge
    equipped_badge = db.relationship(
        "Badge",
        foreign_keys=[equipped_badge_id],
        post_update=True
    )


    def get_current_level_badge(self):
        """Get the highest badge user has earned based on XP"""
        from app.models.badge import Badge, UserBadge
        
        # Get all earned badges
        earned_badges = UserBadge.query.filter_by(user_id=self.id).all()
        earned_badge_ids = [eb.badge_id for eb in earned_badges]
        
        if not earned_badge_ids:
            return None
            
        # Get the highest XP threshold badge that user has earned
        badge = Badge.query.filter(
            Badge.id.in_(earned_badge_ids)
        ).order_by(Badge.xp_threshold.desc()).first()
        
        return badge
    
    def get_highest_earned_badge(self):
        """Get the badge with highest XP threshold that user qualifies for"""
        from app.models.badge import Badge
        badge = Badge.query.filter(
            Badge.xp_threshold <= self.xp
        ).order_by(Badge.xp_threshold.desc()).first()
        return badge
    
    def get_all_earned_badges(self):
        """Get all badges user has earned"""
        from app.models.badge import UserBadge
        return UserBadge.query.filter_by(user_id=self.id).all()
    
    def check_and_award_badges(self):
        """Check if user qualifies for new badges based on XP"""
        from app.models.badge import Badge, UserBadge
        from app.extensions import db
        
        # Get all badges ordered by XP threshold
        all_badges = Badge.query.order_by(Badge.xp_threshold.asc()).all()
        
        # Get already earned badges
        earned_badges = self.get_all_earned_badges()
        earned_badge_ids = [eb.badge_id for eb in earned_badges]
        
        new_badges_awarded = []
        
        for badge in all_badges:
            # Check if user qualifies for this badge and hasn't earned it yet
            if self.xp >= badge.xp_threshold and badge.id not in earned_badge_ids:
                # Award new badge
                user_badge = UserBadge(
                    user_id=self.id,
                    badge_id=badge.id
                )
                db.session.add(user_badge)
                new_badges_awarded.append(badge)
                print(f"Awarded badge {badge.name} to user {self.username}")
        
        if new_badges_awarded:
            db.session.commit()
            print(f"Committed {len(new_badges_awarded)} new badges")
        
        return new_badges_awarded
    
    def add_xp(self, amount):
        """Add XP to user and check for new badges"""
        self.xp += amount
        db.session.add(self)
        db.session.commit()
        
        # Check for new badges
        new_badges = self.check_and_award_badges()
        return new_badges
    
    def __repr__(self):
        return f"<User {self.username} XP:{self.xp}>"
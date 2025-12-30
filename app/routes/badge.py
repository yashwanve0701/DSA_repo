from flask import Blueprint, render_template, jsonify, request, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.badge import Badge, UserBadge
from app.models.user import User

badge_bp = Blueprint("badge", __name__, url_prefix="/badges")

# Initialize default badges (run this once to populate database)
DEFAULT_BADGES = [
    {
        "name": "Code Newbie",
        "description": "Started your coding journey!",
        "icon": "👶",
        "xp_threshold": 10,
        "color": "bronze",
        "level": "Beginner"
    },
    {
        "name": "Syntax Sorcerer",
        "description": "Mastered the basics of programming syntax",
        "icon": "🔮",
        "xp_threshold": 50,
        "color": "bronze",
        "level": "Apprentice"
    },
    {
        "name": "Loop Legend",
        "description": "Mastered loops and iterations",
        "icon": "🌀",
        "xp_threshold": 100,
        "color": "silver",
        "level": "Intermediate"
    },
    {
        "name": "Function Pharaoh",
        "description": "Became a master of functions and methods",
        "icon": "👑",
        "xp_threshold": 200,
        "color": "silver",
        "level": "Advanced"
    },
    {
        "name": "Algorithm Alchemist",
        "description": "Transformed algorithms into gold",
        "icon": "⚗️",
        "xp_threshold": 350,
        "color": "gold",
        "level": "Expert"
    },
    {
        "name": "Data Structure Sage",
        "description": "Wisdom in arrays, linked lists, and trees",
        "icon": "🧙",
        "xp_threshold": 500,
        "color": "gold",
        "level": "Master"
    },
    {
        "name": "Debugging Dragon",
        "description": "Burned through bugs with fire",
        "icon": "🐉",
        "xp_threshold": 650,
        "color": "platinum",
        "level": "Legend"
    },
    {
        "name": "Full Stack Phoenix",
        "description": "Rose from the ashes of challenges to master full stack",
        "icon": "🦚",
        "xp_threshold": 850,
        "color": "diamond",
        "level": "Mythic"
    },
    {
        "name": "Boss Coder",
        "description": "The ultimate coding champion!",
        "icon": "🏆",
        "xp_threshold": 1000,
        "color": "legendary",
        "level": "Boss"
    }
]
@badge_bp.route("/")
@login_required
def badge_collection():
    """Show all badges with user's progress"""
    # Ensure badges are initialized
    init_badges()
    
    # Check and award new badges based on current XP
    current_user.check_and_award_badges()
    
    all_badges = Badge.query.order_by(Badge.xp_threshold.asc()).all()
    earned_badges = UserBadge.query.filter_by(user_id=current_user.id).all()
    earned_badge_ids = [eb.badge_id for eb in earned_badges]
    
    equipped_badge = None
    if current_user.equipped_badge_id:
        equipped_badge = Badge.query.get(current_user.equipped_badge_id)
    
    return render_template(
        "badge/collection.html",  # Changed from "badge/collection.html"
        all_badges=all_badges,
        earned_badge_ids=earned_badge_ids,
        current_xp=current_user.xp,
        equipped_badge=equipped_badge,
        user=current_user
    )

@badge_bp.route("/equip/<int:badge_id>", methods=["POST"])
@login_required
def equip_badge(badge_id):
    """Equip a badge (user has earned it)"""
    # Check if user has earned this badge
    user_badge = UserBadge.query.filter_by(
        user_id=current_user.id,
        badge_id=badge_id
    ).first()
    
    if not user_badge:
        return jsonify({"success": False, "message": "Badge not earned yet!"}), 400
    
    current_user.equipped_badge_id = badge_id
    db.session.commit()
    
    return jsonify({"success": True, "message": "Badge equipped!"})

@badge_bp.route("/unequip", methods=["POST"])
@login_required
def unequip_badge():
    """Unequip current badge"""
    current_user.equipped_badge_id = None
    db.session.commit()
    return jsonify({"success": True, "message": "Badge unequipped!"})

@badge_bp.route("/init-badges")
def init_badges():
    """Initialize badges in database (run this once)"""
    try:
        for badge_data in DEFAULT_BADGES:
            existing = Badge.query.filter_by(name=badge_data["name"]).first()
            if not existing:
                badge = Badge(**badge_data)
                db.session.add(badge)
                print(f"Added badge: {badge_data['name']}")
        
        db.session.commit()
        print("Badges initialized successfully!")
        return jsonify({"success": True, "message": "Badges initialized!"})
    except Exception as e:
        print(f"Error initializing badges: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
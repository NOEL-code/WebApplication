from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    matching_preferences = db.relationship("MatchingPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sent_proposals = db.relationship("DateProposal", back_populates="proposer", foreign_keys="DateProposal.proposer_id")
    received_proposals = db.relationship("DateProposal", back_populates="recipient", foreign_keys="DateProposal.recipient_id")
    likes = db.relationship("User", secondary="likes", primaryjoin="User.id == likes.c.liker_id", secondaryjoin="User.id == likes.c.liked_id", back_populates="liked_by")
    blocks = db.relationship("User", secondary="blocks", primaryjoin="User.id == blocks.c.blocker_id", secondaryjoin="User.id == blocks.c.blocked_id", back_populates="blocked_by")

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    birth_year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    photo_path = db.Column(db.String(255))

    user = db.relationship("User", back_populates="profile")

class MatchingPreference(db.Model):
    __tablename__ = 'matching_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    preferred_genders = db.Column(db.Text, nullable=False)
    min_age = db.Column(db.Integer, nullable=False)
    max_age = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", back_populates="matching_preferences")

likes = db.Table(
    'likes',
    db.Column('liker_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('liked_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

blocks = db.Table(
    'blocks',
    db.Column('blocker_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('blocked_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class DateProposal(db.Model):
    __tablename__ = 'date_proposals'
    id = db.Column(db.Integer, primary_key=True)
    proposer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    proposed_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="proposed")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    proposal_message = db.Column(db.Text)
    response_message = db.Column(db.Text)

    proposer = db.relationship("User", back_populates="sent_proposals", foreign_keys=[proposer_id])
    recipient = db.relationship("User", back_populates="received_proposals", foreign_keys=[recipient_id])
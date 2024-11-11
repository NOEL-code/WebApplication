from . import db
from flask_login import UserMixin
from datetime import datetime
import enum

# Enum for date proposal status
class ProposalStatus(enum.Enum):
    proposed = 1
    accepted = 2
    rejected = 3
    ignored = 4
    reschedule = 5

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile = db.relationship("Profile", back_populates="user", uselist=False)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    name = db.Column(db.String(50))
    gender = db.Column(db.String(20))
    year_of_birth = db.Column(db.Integer)
    description = db.Column(db.Text)
    user = db.relationship("User", back_populates="profile")

class DateProposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.DateTime)
    status = db.Column(db.Enum(ProposalStatus), default=ProposalStatus.proposed)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

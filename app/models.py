from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Date, DateTime, Enum, Table

db = SQLAlchemy()

# 열거형 데이터 타입 정의
class ProposalStatus(enum.Enum):
    proposed = 1
    accepted = 2
    rejected = 3
    ignored = 4
    reschedule = 5

# 사용자 모델
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    matching_preferences = relationship("MatchingPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sent_proposals = relationship("DateProposal", back_populates="proposer", foreign_keys="DateProposal.proposer_id")
    received_proposals = relationship("DateProposal", back_populates="recipient", foreign_keys="DateProposal.recipient_id")
    likes = relationship("User", secondary="likes", primaryjoin="User.id == likes.c.liker_id", secondaryjoin="User.id == likes.c.liked_id", back_populates="liked_by")
    liked_by = relationship("User", secondary="likes", primaryjoin="User.id == likes.c.liked_id", secondaryjoin="User.id == likes.c.liker_id", back_populates="likes")
    blocks = relationship("User", secondary="blocks", primaryjoin="User.id == blocks.c.blocker_id", secondaryjoin="User.id == blocks.c.blocked_id", back_populates="blocked_by")
    blocked_by = relationship("User", secondary="blocks", primaryjoin="User.id == blocks.c.blocked_id", secondaryjoin="User.id == blocks.c.blocker_id", back_populates="blocks")

# 프로필 모델
class Profile(db.Model):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    gender = Column(String(50), nullable=False)
    birth_year = Column(Integer, nullable=False)
    description = Column(Text)
    photo_path = Column(String(255))

    user = relationship("User", back_populates="profile")

# 매칭 선호도 모델
class MatchingPreference(db.Model):
    __tablename__ = 'matching_preferences'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    preferred_genders = Column(Text, nullable=False)
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)

    user = relationship("User", back_populates="matching_preferences")

# 좋아요 테이블
likes = Table(
    'likes',
    db.Column('liker_id', Integer, ForeignKey('users.id'), primary_key=True),
    db.Column('liked_id', Integer, ForeignKey('users.id'), primary_key=True),
    db.UniqueConstraint('liker_id', 'liked_id', name='unique_like')
)

# 차단 테이블
blocks = Table(
    'blocks',
    db.Column('blocker_id', Integer, ForeignKey('users.id'), primary_key=True),
    db.Column('blocked_id', Integer, ForeignKey('users.id'), primary_key=True),
    db.UniqueConstraint('blocker_id', 'blocked_id', name='unique_block')
)

# 데이트 제안 모델
class DateProposal(db.Model):
    __tablename__ = 'date_proposals'
    id = Column(Integer, primary_key=True)
    proposer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    proposed_date = Column(Date, nullable=False)
    status = Column(Enum(ProposalStatus), nullable=False, default=ProposalStatus.proposed)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime)
    proposal_message = Column(Text, nullable=True)
    response_message = Column(Text, nullable=True)

    proposer = relationship("User", back_populates="sent_proposals", foreign_keys=[proposer_id])
    recipient = relationship("User", back_populates="received_proposals", foreign_keys=[recipient_id])
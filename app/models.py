from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum, Date, DateTime, Table
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app import db

# Enum 정의
class GenderEnum(PyEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class ProposalStatusEnum(PyEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IGNORED = "ignored"
    RESCHEDULED = "rescheduled"

# 다대다 관계 테이블 정의
liked_users = Table(
    'liked_users',
    db.metadata,  # metadata를 명시적으로 지정
    db.Column('liker_id', Integer, ForeignKey('users.id'), primary_key=True),
    db.Column('liked_id', Integer, ForeignKey('users.id'), primary_key=True)
)

blocked_users = Table(
    'blocked_users',
    db.metadata,  # metadata를 명시적으로 지정
    db.Column('blocker_id', Integer, ForeignKey('users.id'), primary_key=True),
    db.Column('blocked_id', Integer, ForeignKey('users.id'), primary_key=True)
)

# 사용자 모델
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    matching_preference = relationship("MatchingPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sent_proposals = relationship("DateProposal", back_populates="proposer", foreign_keys="DateProposal.proposer_id")
    received_proposals = relationship("DateProposal", back_populates="recipient", foreign_keys="DateProposal.recipient_id")
    liked_users = relationship(
        'User',
        secondary=liked_users,
        primaryjoin=(liked_users.c.liker_id == id),
        secondaryjoin=(liked_users.c.liked_id == id),
        backref='liked_by'
    )
    blocked_users = relationship(
        'User',
        secondary=blocked_users,
        primaryjoin=(blocked_users.c.blocker_id == id),
        secondaryjoin=(blocked_users.c.blocked_id == id),
        backref='blocked_by'
    )

# 사용자 프로필 모델
class Profile(db.Model):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    gender = Column(Enum(GenderEnum, native_enum=False), nullable=False)
    birth_year = Column(Integer, nullable=False)
    description = Column(Text)
    photo = relationship("Photo", uselist=False, back_populates="profile")

    user = relationship("User", back_populates="profile")

# 매칭 선호도 모델
class MatchingPreference(db.Model):
    __tablename__ = 'matching_preferences'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    preferred_genders = Column(String(50), nullable=False)  # 콤마로 구분된 문자열로 저장
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)

    user = relationship("User", back_populates="matching_preference")

# 데이트 제안 모델
class DateProposal(db.Model):
    __tablename__ = 'date_proposals'
    id = Column(Integer, primary_key=True)
    proposer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    proposed_date = Column(Date, nullable=False)
    status = Column(Enum(ProposalStatusEnum, native_enum=False), default=ProposalStatusEnum.PROPOSED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)  # 응답 시간이 있을 경우 저장
    proposal_message = Column(Text, nullable=True)  # 제안 메시지
    response_message = Column(Text, nullable=True)  # 응답 메시지

    proposer = relationship("User", back_populates="sent_proposals", foreign_keys=[proposer_id])
    recipient = relationship("User", back_populates="received_proposals", foreign_keys=[recipient_id])

# 사진 모델
class Photo(db.Model):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    file_extension = Column(String(8), nullable=False)  # 확장자: jpg, png 등

    profile = relationship("Profile", back_populates="photo")
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class UserStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class NewsCategory(str, enum.Enum):
    tech = "Texnologiya"
    sport = "Sport"
    politics = "Siyosat"
    economy = "Iqtisodiyot"
    world = "Dunyo"
    culture = "Madaniyat"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.user)
    status = Column(String(20), default=UserStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="author")

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, index=True)
    summary = Column(String(500))
    content = Column(Text, nullable=False)
    category = Column(String(50), default=NewsCategory.tech)
    image_url = Column(String(300), default="/static/images/default.jpg")
    is_published = Column(Boolean, default=True)
    views = Column(Integer, default=0)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="news")

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    urls = relationship("Url", back_populates="owner")


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_url = Column(String, index=True, unique=True, nullable=False)
    long_url = Column(String, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created = Column(DateTime, index=True)
    expiration_time = Column(Integer, index=True)  # timedelta expressed in seconds
    last_access = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True)
    deleted = Column(DateTime, index=True)
    campaign = Column(String, index=True)

    owner = relationship("User", back_populates="urls")
    clicks = relationship("Click", back_populates="link")


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("urls.id"))
    visited = Column(DateTime, index=True)
    referer = Column(String, index=True)
    user_agent = Column(String, index=True)
    viewport = Column(String, index=True)

    link = relationship("Url", back_populates="clicks")

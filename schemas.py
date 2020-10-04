from datetime import datetime, timedelta

from typing import List, Optional
from pydantic import BaseModel


class ClickBase(BaseModel):
    visited: datetime
    referer: Optional[str] = None
    user_agent: Optional[str] = None
    viewport: Optional[str] = None


class ClickCreate(ClickBase):
    pass


class Click(ClickBase):
    id: int
    link_id: int

    class Config:
        orm_mode = True


class UrlBase(BaseModel):
    short_url: str
    long_url: str
    created: datetime
    expiration_time: timedelta
    last_access: datetime
    is_active: bool
    deleted: datetime = None
    campaign: str


class UrlCreate(UrlBase):
    pass


class Url(UrlBase):
    id: int
    owner_id: int
    clicks: List[Click] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    urls: List[Url] = []

    class Config:
        orm_mode = True
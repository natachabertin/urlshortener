from sqlalchemy.orm import Session

import models
import schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_urls(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Url).offset(skip).limit(limit).all()


def get_url_by_shortened(db: Session, short_url: str):
    return db.query(models.Url).filter(models.Url.short_url == short_url).first()


def create_user_url(db: Session, url: schemas.UrlCreate, user_id: int):
    db_url = models.Url(**url.dict(), owner_id=user_id)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_clicks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Click).offset(skip).limit(limit).all()


def create_url_click(db: Session, click: schemas.ClickCreate, url_id: int):
    db_click = models.Click(**click.dict(), link_id=url_id)
    db.add(db_click)
    db.commit()
    db.refresh(db_click)
    return db_click

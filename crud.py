import secrets

from sqlalchemy.orm import Session

import models
import schemas
from errors import WrongPasswordException
from utils import hash_password, verify_password, generate_random_short_url


def validate_user(db: Session, credentials):
    user = get_user_by_email(db, credentials.username)
    if user is None:
        raise ValueError("Wrong username. Use your email.")
    if not verify_password(user.password, credentials.password):
        raise WrongPasswordException("Password incorrect.")

    return user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_urls(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Url).filter(models.Url.is_active).offset(skip).limit(limit).all()


def get_url_by_shortened(db: Session, short_url: str):
    return db.query(models.Url).filter(models.Url.short_url == short_url, models.Url.is_active == True).first()


def create_user_url(db: Session, url: schemas.UrlCreate, user_id: int):
    if url.short_url is None:
        url.short_url = generate_random_short_url()
    if not url_already_exists(db, url.short_url):
        db_url = models.Url(**url.dict(), owner_id=user_id)
        db.add(db_url)
        db.commit()
        db.refresh(db_url)
        return db_url
    else:
        raise ValueError('That URL is taken.')


def get_clicks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Click).offset(skip).limit(limit).all()


def create_url_click(db: Session, click: schemas.ClickCreate, url_id: int):
    db_click = models.Click(**click.dict(), link_id=url_id)
    db.add(db_click)
    db.commit()
    db.refresh(db_click)
    return db_click


def disable_url(db: Session, url_id: int):
    url = db.query(models.Url).filter(models.Url.id == url_id).first()
    if url is None:
        raise ValueError("Url not found")
    url.is_active = False
    db.commit()
    db.refresh(url)
    return url


def url_already_exists(db: Session, short_url: str):
    """
    Validation for custom named short Urls.
    Checks the DB and returns if the short url is occupied.

    Params:
    -------
    db : Session
        Current database. Mandatory.

    short_url : str
        Short URL to validate if already exists.
        Mandatory.

    Returns:
    --------
    Bool
    """
    return get_url_by_shortened(db, short_url) is not None

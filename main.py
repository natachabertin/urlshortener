"""
Run server from console with:
uvicorn main:app --reload
"""
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine
from errors import WrongPasswordException

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="URL shortener")


# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    # TODO: improve the user feedback!
    try:
        return crud.validate_user(db, credentials)
    except (ValueError, WrongPasswordException) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err.args[0],
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get("/")
async def read_main():
    return {"msg": "URL shortener"}


@app.get("/{short_url}")
def access_url(short_url: str, request: Request, db: Session = Depends(get_db)):
    url = crud.get_url_by_shortened(db, short_url)
    if url is None:
        raise HTTPException(status_code=404, detail="That link doesn't exist.")
    headers = request.headers
    click = schemas.ClickCreate(
        visited=datetime.now(),
        user_agent=headers.get('user-agent'),
        # Some other examples as Client Hints, etc. added this 2 to validate NAN behavior.
        referer=headers.get('referer'),
        viewport=headers.get('viewport')
    )
    crud.create_url_click(db=db, click=click, url_id=url.id)
    return RedirectResponse(url.long_url)


@app.get("/users/me", response_model=schemas.User)
def current_user_data(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns current user profile (user, urls and associated clicks)."""
    return crud.get_user(db, user_id=user.id)


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/urls/", response_model=schemas.Url)
def create_url_for_user(user_id: int, url: schemas.UrlCreate, db: Session = Depends(get_db)):
    return crud.create_user_url(db=db, url=url, user_id=user_id)


@app.get("/urls/", response_model=List[schemas.Url])
def read_urls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    urls = crud.get_urls(db, skip=skip, limit=limit)
    return urls


@app.delete("/urls/{url_id}", response_model=schemas.Url)
def delete_url(url_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    # TODO: refactor this ugliness
    try:
        return crud.disable_url(db, url_id=url_id)
    except ValueError:
        raise HTTPException(status_code=418, detail="Invalid URL can't be deleted")


@app.get("/clicks/", response_model=List[schemas.Click])
def read_clicks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clicks = crud.get_clicks(db, skip=skip, limit=limit)
    return clicks


# we need this main to debug it
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

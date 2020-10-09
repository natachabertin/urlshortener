"""
Run server from console with:
uvicorn main:app --reload
"""
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException  # , Request, Response
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="URL shortener")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# with this MDW we can work async with SQLite (opens a DB on each req and close it to unblock)
# @app.middleware("http")
# async def db_session_middleware(request: Request, call_next):
#     response = Response("Internal server error", status_code=500)
#     try:
#         request.state.db = SessionLocal()
#         response = await call_next(request)
#     finally:
#         request.state.db.close()
#     return response

# # Dependency
# def get_db(request: Request):
#     return request.state.db

@app.get("/")
async def read_main():
    return {"msg": "URL shortener"}


@app.get("/{short_url}")
# def access_url(short_url: str, click: schemas.ClickCreate, db: Session = Depends(get_db)):
def access_url(short_url: str, db: Session = Depends(get_db)):
    url = crud.get_url_by_shortened(db, short_url)
    click = schemas.ClickCreate(
        visited=datetime.now(),
        referer="string",
        user_agent="string",
        viewport="string"
    )
    crud.create_url_click(db=db, click=click, url_id=url.id)
    return RedirectResponse(url.long_url)


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


@app.post("/urls/{url_id}/clicks/", response_model=schemas.Click)
def create_click_for_url(url_id: int, click: schemas.ClickCreate, db: Session = Depends(get_db)):
    return crud.create_url_click(db=db, click=click, url_id=url_id)


@app.get("/clicks/", response_model=List[schemas.Click])
def read_clicks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clicks = crud.get_clicks(db, skip=skip, limit=limit)
    return clicks


# we need this main to debug it
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

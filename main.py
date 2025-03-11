from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import EmailStr
from sqlmodel import Field, Session, SQLModel, select
from .database import (
    create_db_and_tables, 
    drop_all_tables, 
    engine,
    get_session
)
from typing import Annotated


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str
    role: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_disabled: bool = Field(default=False)


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    drop_all_tables() # Uncomment this line to drop all existing tables
    create_db_and_tables() # Ensure all tables exists
    

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/users/")
def create_user(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
from datetime import datetime, timezone
from enum import Enum
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import EmailStr
from sqlmodel import Field, Session, SQLModel, select
from .database import (
    create_db_and_tables, 
    drop_all_tables, 
    get_session
)
from typing import Annotated


class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    # USER = "user"


class UserBase(SQLModel):
    email: EmailStr


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str
    role: UserRole
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_disabled: bool = Field(default=False)


class UserPublic(UserBase):
    id: int
    role: UserRole


class UserCreate(UserBase):
    password: str
    role: UserRole = Field(default=UserRole.EDITOR)  # Default to 'editor'


class UserUpdate(UserBase):
    email: EmailStr | None = None
    password: str | None = None
    is_disabled: bool | None = None # Only admin has permission


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


# Function to hash password
#TODO Implement proper hashing code
def hash_password(password: str) -> str:
    return f"Hashed {password}"


@app.on_event("startup")
def on_startup():
    drop_all_tables() # Uncomment this line to drop all existing tables
    create_db_and_tables() # Ensure all tables exists


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/users/", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    hashed_password = hash_password(user.password)
    extra_data = {"hashed_password": hashed_password}
    db_user = User.model_validate(user, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get("/users/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@app.get("/users/{user_id}", response_model=UserPublic)
def read_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: UserUpdate, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = hash_password(password)
        extra_data["hashed_password"] = hashed_password
    user_db.sqlmodel_update(user_data, update=extra_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
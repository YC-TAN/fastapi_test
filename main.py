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
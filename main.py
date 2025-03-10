from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str
    role: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_disabled: bool = Field(default=False)


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
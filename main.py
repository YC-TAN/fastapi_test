from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import EmailStr
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str
    role: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_disabled: bool = Field(default=False)


sqlite_file_name = "test.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def drop_all_tables():
    SQLModel.metadata.drop_all(engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
def on_startup():
    # drop_all_tables() # Uncomment this line to drop all existing tables
    create_db_and_tables() # Ensure all tables exists
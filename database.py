from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

DB_NAME = "test_user"
db_url = "postgresql://postgres:test1234@localhost:5432/test_user"
DATABASE_URL = "postgresql+asyncpg://postgres:test1234@localhost:5432/test_user"

engine = create_engine(db_url, echo=True)

# sqlite_file_name = "test.db"
# file_name = os.getenv("SQL_FILE_NAME")
# sqlite_url = f"sqlite:///{file_name}"

# connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, connect_args=connect_args)


def drop_all_tables():
    SQLModel.metadata.drop_all(engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
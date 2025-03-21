from fastapi import FastAPI
from .database import (
    create_db_and_tables, 
    drop_all_tables, 
)
from .routes import user, auth
from fastapi.middleware.cors import CORSMiddleware

# from . import utils


app = FastAPI()


origins = [
    "http://localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    drop_all_tables() # Uncomment this line to drop all existing tables
    create_db_and_tables() # Ensure all tables exists


# Routers for API endpoints
app.include_router(user.router)
app.include_router(auth.router)
from uuid import uuid4
from fastapi import FastAPI, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from utils.sql_api import DB
from models import Gift, User
from auth import *
from routers import gifts, users, db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(gifts.router)
app.include_router(users.router)

@app.on_event("shutdown")
def shutdown_event():
    db.close()
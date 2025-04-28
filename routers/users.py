import os

import shortuuid
from fastapi import APIRouter, HTTPException, status
from utils.auth import get_password_hash, verify_password, create_access_token
from . import db
from models.User import User
from utils.config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

PRODUCTION = bool(int(os.getenv("PRODUCTION")))
URL = "/api/" if PRODUCTION else "/"

@router.get(URL + "users/")
async def get_users() -> dict[str, list[User]]:
    users = db.get_all_users()
    return {"users": users}


@router.get(URL + "users/{user_id}")
async def get_user_by_id(user_id: str) -> dict[str, User]:
    user = db.get_user_by_id(user_id)
    return {"user": user}


@router.post(URL + "register")
async def register(user: dict) -> dict[str, str]:
    existing_user = db.get_user_by_username(user["username"])
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    new_user = {
        "user_id": str(shortuuid.uuid(name=user["username"])),
        "username": user["username"],
        "password": get_password_hash(user["password"]),
    }
    db.create_user(new_user)
    return {"message": "User registered successfully."}


@router.post(URL + "login")
async def login(credentials: dict) -> dict[str, str]:
    user = db.get_user_by_username(credentials["username"])
    if not user or not verify_password(credentials["password"], user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": credentials["username"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user["user_id"],
    }

import os
import shortuuid
from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from dotenv import load_dotenv

from utils.auth import get_password_hash, verify_password, create_access_token
from . import db, logger
from models.User import User
from utils.config import ACCESS_TOKEN_EXPIRE_MINUTES

load_dotenv()
router = APIRouter()

PRODUCTION = bool(int(os.getenv("PRODUCTION")))
URL = "/api/" if PRODUCTION else "/"


@router.get(URL + "users/")
async def get_users() -> dict[str, list[User]]:
    try:
        logger.info("Attempting to fetch all users")
        users = db.get_all_users()
        logger.success(f"Successfully fetched {len(users)} users")
        return {"users": users}
    except Exception as e:
        logger.error(f"Failed to fetch users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users",
        )


@router.get(URL + "users/{user_id}")
async def get_user_by_id(user_id: str) -> dict[str, User]:
    try:
        logger.info(f"Attempting to fetch user with ID: {user_id}")
        user = db.get_user_by_id(user_id)

        if not user:
            logger.warning(f"User not found with ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        logger.success(f"Successfully fetched user: {user['username']}")
        return {"user": user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user",
        )


@router.post(URL + "register")
async def register(user: dict) -> dict[str, str]:
    try:
        logger.info(f"Attempting to register new user: {user.get('username')}")

        if not user.get("username") or not user.get("password"):
            logger.warning("Registration attempt with missing username or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required",
            )

        existing_user = db.get_user_by_username(user["username"])
        if existing_user:
            logger.warning(f"Username already exists: {user['username']}")
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
        logger.success(f"User registered successfully: {user['username']}")
        return {"message": "User registered successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register user {user.get('username')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@router.post(URL + "login")
async def login(credentials: dict) -> dict[str, str]:
    try:
        logger.info(f"Login attempt for username: {credentials.get('username')}")

        if not credentials.get("username") or not credentials.get("password"):
            logger.warning("Login attempt with missing username or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required",
            )

        user = db.get_user_by_username(credentials["username"])
        if not user:
            logger.warning(f"Login failed - user not found: {credentials['username']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(credentials["password"], user["password"]):
            logger.warning(
                f"Login failed - invalid password for user: {credentials['username']}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            data={"sub": credentials["username"]},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        logger.success(f"User logged in successfully: {credentials['username']}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["user_id"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {credentials.get('username')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )

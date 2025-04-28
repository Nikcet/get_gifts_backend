import os
from uuid import uuid4
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, Request

from utils.auth import get_current_user
from utils.parsers import parse_url_ozon
from models.Gift import Gift
from . import db
from loguru import logger

logger.add(
    "logs.log",
    rotation="10 MB",
    retention="15 days",
    compression="zip",
    level="INFO"
)

load_dotenv()
router = APIRouter()

PRODUCTION = bool(int(os.getenv("PRODUCTION")))
URL = "/api/" if PRODUCTION else "/"

@router.get(URL + "gifts/")
async def get_gifts() -> dict[str, list[Gift]]:
    logger.info("Запрос на получение всех подарков")
    gifts = db.get_all_gifts()
    logger.info(gifts)
    return {"gifts": gifts}


@router.get(URL + "gifts/{id}")
async def get_gift(id: str) -> dict[str, Gift]:
    gift = db.get_gift_by_id(id)
    if gift:
        return {"gift": gift}
    raise HTTPException(status_code=404, detail="The gift does not exist.")


@router.get(URL + "gifts/user/{user_id}")
async def get_gifts_by_user(user_id: str) -> dict[str, list[Gift]]:
    gifts = db.get_gifts_by_user_id(user_id)
    return {"gifts": gifts}


@router.post(URL + "gifts/", dependencies=[Depends(get_current_user)])
async def add_gift(request: Request, data: dict[str, str]) -> dict[str, str]:
    logger.info("Запрос на добавление подарка: ", data)
    
    token = request.headers.get("Authorization").replace("Bearer ", "")
    current_user = await get_current_user(token)

    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")

    new_gift = {}

    if "ozon.ru" in data["link"]:
        try:
            logger.info("Start to parse OZON.")
            new_gift = await parse_url_ozon(data["link"])
            logger.info("Parsing is success. Start to collect new_gift.")
        except Exception as e:
            logger.error(f"Error while parsing OZON, {e}")
            raise HTTPException(status_code=422, detail=f"Failed to add the gift. {e}")

    try:
        new_gift["id"] = str(uuid4())
        new_gift["user_id"] = current_user["user"]["user_id"]
        new_gift["is_reserved"] = False
        new_gift["reserve_owner"] = ""
        new_gift["link"] = data["link"]
    except Exception as e:
        logger.error(f"Error while collect new_gift, {e}")
        raise HTTPException(status_code=422, detail=f"Failed to add the gift. {e}")
    
    try: 
        db.add_gift(new_gift)
        logger.info("new_gift добавлен в БД.")
        return {"message": "Gift added successfully."}
    except Exception as e:
        logger.error(f"Error while adding gift to DB: {e}")
        raise HTTPException(status_code=422, detail=f"Failed to add the gift. {e}")


@router.put(URL + "gifts/{id}")
async def update_gift(id: str, updated_gift: Gift) -> dict:
    db.update_gift(id, updated_gift.dict())
    return {"message": "Gift updated successfully."}


@router.delete(URL + "gifts/{id}")
async def delete_gift(id: str) -> dict:
    db.delete_gift(id)
    return {"message": f"Gift {id} deleted successfully."}

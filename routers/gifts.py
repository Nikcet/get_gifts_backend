from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends, Request
from utils.parsers import parse_url_ozon
from models import Gift
from auth import get_current_user
from . import db


router = APIRouter()


@router.get("/gifts/")
async def get_gifts() -> dict[str, list[Gift]]:
    gifts = db.get_all_gifts()
    return {"gifts": gifts}


@router.get("/gifts/{id}")
async def get_gift(id: str) -> dict[str, Gift]:
    gift = db.get_gift_by_id(id)
    if gift:
        return {"gift": gift}
    raise HTTPException(status_code=404, detail="The gift does not exist.")


@router.get("/gifts/user/{user_id}")
async def get_gifts_by_user(user_id: str) -> dict[str, list[Gift]]:
    gifts = db.get_gifts_by_user_id(user_id)
    return {"gifts": gifts}


@router.post("/gifts/", dependencies=[Depends(get_current_user)])
async def add_gift(request: Request, gift_link: dict[str, str]) -> dict[str, str]:
    token = request.headers.get("Authorization").replace("Bearer ", "")
    current_user = await get_current_user(token)

    if not token:
        raise HTTPException(status_code=401, detail="Token not provided")

    new_gift = {}

    # парсинг данных с ozon
    if "ozon.ru" in gift_link["link"]:
        new_gift = await parse_url_ozon(gift_link["link"])

    new_gift["id"] = str(uuid4())
    new_gift["user_id"] = current_user["user"]["user_id"]
    new_gift["is_reserved"] = False
    new_gift["reserve_owner"] = ""
    new_gift["link"] = gift_link["link"]

    db.add_gift(new_gift)

    return {"message": "Gift added successfully."}


@router.put("/gifts/{id}")
async def update_gift(id: str, updated_gift: Gift) -> dict:
    db.update_gift(id, updated_gift.dict())
    return {"message": "Gift updated successfully."}


@router.delete("/gifts/{id}", dependencies=[Depends(get_current_user)])
async def delete_gift(id: str) -> dict:
    db.delete_gift(id)
    return {"message": f"Gift {id} deleted successfully."}

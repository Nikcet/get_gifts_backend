import os
from uuid import uuid4
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, Request, status

from utils.auth import get_current_user
from models.Gift import Gift
from . import db, logger
from tasks import parse_ozon_task

load_dotenv()
router = APIRouter()

PRODUCTION = bool(int(os.getenv("PRODUCTION")))
URL = "/api/" if PRODUCTION else "/"


@router.get(URL + "gifts/")
async def get_gifts() -> dict[str, list[Gift]]:
    try:
        logger.info("Request to get all gifts")
        gifts = db.get_all_gifts()

        if not gifts:
            logger.info("No gifts found in database")
            return {"gifts": []}

        logger.success(f"Successfully fetched {len(gifts)} gifts")
        return {"gifts": gifts}
    except Exception as e:
        logger.error(f"Failed to get gifts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch gifts",
        )


@router.get(URL + "gifts/{id}")
async def get_gift(id: str) -> dict[str, Gift]:
    try:
        logger.info(f"Request to get gift with ID: {id}")
        gift = db.get_gift_by_id(id)

        if not gift:
            logger.warning(f"Gift not found with ID: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Gift not found"
            )

        logger.success(f"Successfully fetched gift: {id}")
        return {"gift": gift}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get gift {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch gift",
        )


@router.get(URL + "gifts/user/{user_id}")
async def get_gifts_by_user(user_id: str) -> dict[str, list[Gift]]:
    try:
        user = db.get_user_by_id(user_id)
        if user is None: 
            raise
        logger.info(f"Find user: {user_id}")
    except Exception as e:
        logger.error(f"Failed to find user by user_id {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to find user by user_id",
        )

    try:
        logger.info(f"Request to get gifts for user: {user_id}")
        gifts = db.get_gifts_by_user_id(user_id)

        if not gifts:
            logger.info(f"No gifts found for user: {user_id}")
            return {"gifts": []}

        logger.success(f"Found {len(gifts)} gifts for user: {user_id}")
        return {"gifts": gifts}

    except Exception as e:
        logger.error(f"Failed to get gifts for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user gifts",
        )


@router.post(URL + "gifts/", dependencies=[Depends(get_current_user)])
async def add_gift(request: Request, data: dict[str, str]) -> dict[str, str]:
    try:
        logger.info("Starting gift addition process")

        if not data.get("link"):
            logger.warning("Attempt to add gift without link")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Link is required"
            )

        token = request.headers.get("Authorization")
        if not token:
            logger.warning("Unauthorized gift addition attempt")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization token missing",
            )

        current_user = await get_current_user(token.replace("Bearer ", ""))

        if "ozon.ru" in data["link"]:
            try:
                gift_id = str(uuid4())
                logger.info(f"Parsing OZON link: {data['link']}")
                task = parse_ozon_task(
                    data["link"], current_user["user"]["user_id"], gift_id
                )
                return {"task_id": task.id, "gift_id": gift_id, "status": "processing"}
                # new_gift = await parse_url_ozon(data["link"])
                logger.info("OZON parsing task is started.")
            except Exception as e:
                logger.error(f"Failed to queue parsing task: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to start parsing process",
                )

        # try:
        #     new_gift = {
        #         "id": str(uuid4()),
        #         "user_id": current_user["user"]["user_id"],
        #         "is_reserved": False,
        #         "reserve_owner": "",
        #         "link": data["link"],
        #         "name": "",
        #         "photo": "",
        #         "cost": ""
        #     }
        #     logger.success(f"Gift added: {new_gift['id']}")
        # except Exception as e:
        #     logger.error(f"Gift object creation failed: {str(e)}")
        #     raise HTTPException(
        #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        #         detail="Invalid gift data structure",
        #     ) from e

        # try:
        #     db.add_gift(new_gift)
        #     logger.success(f"Gift added successfully: {new_gift['id']}")
        #     return {"message": "Gift added successfully."}
        # except Exception as e:
        #     logger.error(f"Database error: {str(e)}")
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Failed to save gift to database",
        #     ) from e

    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error in add_gift: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.put(URL + "gifts/{id}")
async def update_gift(id: str, updated_gift: Gift) -> dict:
    try:
        logger.info(f"Request to update gift: {id}")

        existing_gift = db.get_gift_by_id(id)
        if not existing_gift:
            logger.warning(f"Update failed - gift not found: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Gift not found"
            )

        try:
            db.update_gift(id, updated_gift.dict())
            logger.success(f"Gift updated successfully: {id}")
            return {"message": "Gift updated successfully."}
        except Exception as e:
            logger.error(f"Update failed for gift {id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update gift",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating gift {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(URL + "gifts/{id}")
async def delete_gift(id: str) -> dict:
    try:
        logger.info(f"Request to delete gift: {id}")

        existing_gift = db.get_gift_by_id(id)
        if not existing_gift:
            logger.warning(f"Delete failed - gift not found: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Gift not found"
            )

        try:
            db.delete_gift(id)
            logger.success(f"Gift deleted successfully: {id}")
            return {"message": f"Gift {id} deleted successfully."}
        except Exception as e:
            logger.error(f"Delete failed for gift {id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete gift",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting gift {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(URL + "gifts/status/{id}")
async def check_status(id: str):
    logger.info(f"Try to get gift with id: {id}")

    gift = db.get_gift_by_id(id)
    logger.info(f"Gift status: {gift}")
    return {"status": "success" if gift else "processing"}

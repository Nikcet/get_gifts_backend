from huey_config import huey
from routers import logger
from utils.parsers import parse_url_ozon
from utils.sql_api import DB

@huey.task()
def parse_ozon_task(link: str, user_id: str, gift_id: str):
    try:
        logger.info(f"Starting OZON parsing for {link}")

        parsed_data = parse_url_ozon(link)

        gift_data = {
            "id": gift_id,
            "user_id": user_id,
            "is_reserved": False,
            "reserve_owner": "",
            "link": link,
            **parsed_data,
        }

        db = DB()
        
        db.add_gift(gift_data)
        logger.success(f"Successfully saved gift {gift_id}")
        return {"status": "success", "gift_id": gift_id}

    except Exception as e:
        logger.error(f"OZON parsing failed: {str(e)}")
        return {"status": "error", "message": str(e)}

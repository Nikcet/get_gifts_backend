from fastapi import FastAPI, HTTPException
import json
from sql_api import DB
from models import Gift, User


app: FastAPI = FastAPI()
db: DB = DB()


@app.get("/gifts/")
async def get_gifts() -> dict[str, list[Gift]]:
    gifts = db.get_all_gifts()
    return {"gifts": gifts}


@app.get("/gifts/{id}")
async def get_gift(id: str) -> Gift:
    gift = db.get_gift_by_id(id)
    if gift:
        return gift
    raise HTTPException(status_code=404, detail="The gift does not exist.")


@app.post("/gifts/")
async def add_gift(new_gift: Gift) -> dict:
    db.add_gift(new_gift.dict())
    return {"message": "Gift added successfully."}


@app.put("/gifts/{id}")
async def update_gift(id: str, updated_gift: Gift) -> dict:
    db.update_gift(id, updated_gift.dict())
    return {"message": "Gift updated successfully."}


@app.delete("/gifts/{id}")
async def delete_gift(id: str, user_id: str) -> dict:
    db.delete_gift(id)
    return {"message": f"Gift {id} deleted successfully."}


@app.on_event("shutdown")
def shutdown_event():
    db.close()

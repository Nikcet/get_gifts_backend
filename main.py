from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sql_api import DB
from models import Gift, User
from auth import *


app = FastAPI()
db = DB()


@app.get("/gifts/")
async def get_gifts() -> dict[str, list[Gift]]:
    gifts = db.get_all_gifts()
    return {"gifts": gifts}


@app.get("/gifts/{id}")
async def get_gift(id: str) -> Gift:
    gift = db.get_gift_by_id(id)
    if gift:
        return {"gift": gift}
    raise HTTPException(status_code=404, detail="The gift does not exist.")


@app.get("/gifts/user/{user_id}")
async def get_gifts_by_user(user_id: str) -> dict[str, list[Gift]]:
    gifts = db.get_gifts_by_user_id(user_id)
    return {"gifts": gifts}


@app.post("/gifts/", dependencies=[Depends(get_current_user)])
async def add_gift(new_gift: Gift) -> dict:
    db.add_gift(new_gift.dict())
    return {"message": "Gift added successfully."}


@app.put("/gifts/{id}", dependencies=[Depends(get_current_user)])
async def update_gift(id: str, updated_gift: Gift) -> dict:
    db.update_gift(id, updated_gift.dict())
    return {"message": "Gift updated successfully."}

@app.delete("/gifts/{id}", dependencies=[Depends(get_current_user)])
async def delete_gift(id: str) -> dict:
    db.delete_gift(id)
    return {"message": f"Gift {id} deleted successfully."}


@app.on_event("shutdown")
def shutdown_event():
    db.close()


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user[2]):  # user[2] - хэш пароля
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}



from fastapi import FastAPI
import json

app: FastAPI = FastAPI()

@app.get("/")
async def get_gifts():
    with open("gifts.json", "r", encoding="utf8") as file:
        gifts = json.load(file)

    return {"gifts": gifts}


@app.get("/{id}")
async def get_gifts(id: str):
    with open("gifts.json", "r", encoding="utf8") as file:
        gifts = json.load(file)

    for gift in gifts:
        if gift["id"] == id:
            return gift

    return {"message": "The gift does not exist."}
    


@app.post("/")
async def add_gift(new_gift: dict):
    with open("gifts.json", "r", encoding="utf8") as file:
        gifts = json.load(file)

    gifts.append(new_gift)

    with open("gifts.json", "w", encoding="utf8") as file:
        json.dump(gifts, file, ensure_ascii=False, indent=4)

    return {"message": "Gift added successfully."}


@app.put("/{id}")
async def update_gift(id: str, new_gift: dict):
    with open("gifts.json", "r", encoding="utf8") as file:
        gifts = json.load(file)

    for gift in gifts:
        if gift["id"] == id:
            gift.update(new_gift)

    with open("gifts.json", "w", encoding="utf8") as file:
        json.dump(gifts, file, ensure_ascii=False, indent=4)

    return {"message": "Gift updated successfully."}


@app.delete("/{id}")
async def delete_gift(id: str):
    with open("gifts.json", "r", encoding="utf8") as file:
        gifts = json.load(file)

    for i, gift in enumerate(gifts):
        if gift["id"] == id:
            del gifts[i]

    with open("gifts.json", "w", encoding="utf8") as file:
        json.dump(gifts, file, ensure_ascii=False, indent=4)

    return {"message": f"Gift {id} deleted successfully."}

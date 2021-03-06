from fastapi import FastAPI,Form,HTTPException
from pydantic import BaseModel
from DBException import UserNotFoundException
import pymongo

app = FastAPI()

#OUATH2
@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin":
        return {"token": "secret-admin-token"}
    else:
        return {"token": "secret-user-token"}


class User(BaseModel):
    username: str
    password: str
    email: str 
    full_name: str
    hashu : str
    receipt_id: str | None = None


def get_user_data(hashu):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = client["mydatabase"]
    usuarios = mydb["users"]
    data = usuarios.find_one({"hashu": hashu})
    if not data:
        raise UserNotFoundException("No se encontro el usuario")
    return data["receipts"]

@app.post("/login/receipts/")
async def get_receipts(user: User):
    hashu = user.hashu
    try:
        data = get_user_data(hashu)
        return {"data":data}
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="El usuario no existe")


@app.delete("/login/receipts")
async def delete_receipt(user: User):
    hashu = user.hashu
    receipt_id = user.receipt_id
    if receipt_id:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = client["mydatabase"]
        usuarios = mydb["users"]
        data = usuarios.find_one({"hashu": hashu})
        if not data:
            raise UserNotFoundException("No se encontro el usuario")
        receipts = data["receipts"]
        for i, receipt in enumerate(receipts):
            if receipt["_id"] == receipt_id:
                receipts.pop(i)
                break
        usuarios.update_one({"hashu": hashu}, {"$set": {"receipts": receipts}})
        return {"data": receipts}

@app.get("/login/promotions/")
async def promotions():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = client["mydatabase"]
    locales = mydb["locales"]
    #Find all promotions
    promotions = []
    for local in locales.find():
        if local["active_promotions"]:
            for promotion in local["active_promotions"]:
            #Logica de si el usuario puede recibir la promocion
                promotions.append(promotion)

    return {"data":promotions}
from fastapi import FastAPI, Form, HTTPException
import pandas as pd
from pydantic import BaseModel
from DBException import UserNotFoundException
from datetime import datetime
import pymongo


app = FastAPI()


#Revisar documentación de como usar ouath2
# @app.post("/login/")
# async def login(username: str = Form(...), password: str = Form(...)):
#     if username == "admin" and password == "admin":
#         return {"token": "secret-admin-token"}
#     else:
#         return {"token": "secret-user-token"}


class User(BaseModel):
    username: str
    password: str
    email: str 
    full_name: str
    hashu : str

#Esto puede cambiar a Elastic Search
def get_db_data(hashu):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = client["mydatabase"]
    locales = mydb["locales"]
    data = locales.find_one({"hashu": hashu})
    if data:
        return data

    raise UserNotFoundException("No se encontro el usuario")

def get_data(hashu):
    try:
        data_user = get_db_data(hashu)
        columns = ["date","client","food","amount"]
        df = pd.DataFrame(data_user["data"], columns=columns)
        return df.to_json()
    except UserNotFoundException as e:
        raise UserNotFoundException(e)


@app.post("/login/dashboard/")
async def data_dashboard(user: User):
    username = user.username
    password = user.password
    hashu = user.hashu
    try:
        data = get_data(hashu)
        return {"data":data}
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail="El usuario no existe")

class nPromotion(BaseModel):
    hashu : str
    name: str
    description: str
    start_date: datetime
    end_date: datetime | None = None
    discount: int
    hashu : str
    
@app.post("/login/dashboard/publish/")
async def publish_data(newPromotion: nPromotion):
    hashu = newPromotion.hashu
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = client["mydatabase"]
    locales = mydb["locales"]
    if not locales.find_one({"hashu": hashu}):
        raise UserNotFoundException("No se encontro el usuario")
    locales.update_one({"hashu": hashu},
    {"$push": {"active_promotions": {"name": newPromotion.name, "description": newPromotion.description, "start_date": newPromotion.start_date, "end_date": newPromotion.end_date, "discount": newPromotion.discount}}})
    return {"data": "Promoción publicada", "promotion":{"name": newPromotion.name, "description": newPromotion.description, "start_date": newPromotion.start_date, "end_date": newPromotion.end_date, "discount": newPromotion.discount} }

    

# @app.get("/login/dashboard/promotions/")
# async def promotions():

class Promotion(BaseModel):
    hashu : str
    name : str

def endPromotion(hashu, name):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = client["mydatabase"]
    locales = mydb["locales"]
    if not locales.find_one({"hashu": hashu, "active_promotions.name": name}):
        raise UserNotFoundException("No se encontro el usuario")
    locales.update_one({"hashu": hashu, "active_promotions.Name":name},
    {"$set": {"promotions.$.end_date": datetime.now()}})
    locales.update_one({"hashu": hashu},
    {"$pull":{"active_promotions":{"name":name}}})
    
    
@app.delete("/login/dashboard/promotions/")
async def promotions(promotion: Promotion):
    hashu = promotion.hashu
    name = promotion.name
    try:
        endPromotion(hashu, name)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail="El usuario no existe")

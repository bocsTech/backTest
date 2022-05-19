from fastapi import FastAPI, Form, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import pandas as pd
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from DBException import UserNotFoundException
from datetime import datetime, timedelta
import pymongo


SECRET_KEY = "d70dc9b88fda2220cb6d9550bcfd0935e11f0409f2ee6e5036a3f6b54b1538c0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#TODO : Hacer los cambios en la base de datos y hacer pruebas de que esta funcionado
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def check_user_DB(username: str):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = client["mydatabase"]
    locales = mydb["locales"]
    data = locales.find_one({"username": username})
    if data:
        return data
    return None

def get_user(username: str):
    user = check_user_DB(username)
    if user:
        user_dict = user
        return UserInDB(**user_dict)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

#Esto puede cambiar a Elastic Search
# ! Hay que revisar si funciona con el nuevo formato de datos 
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

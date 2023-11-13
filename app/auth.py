from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import json

SECRET_KEY = "f38a321f31a41f7d61a1b4076f3a196eb261727a8d833e2a841f04f7948fc92d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 10

json_filename="./app/json/users.json"

with open(json_filename,"r") as read_file:
	users_data = json.load(read_file)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str or None=None

class User(BaseModel):
    user_id: int
    username: str
    name: str or None = None
    password_preprocessed: str

class UserInDB(User):
    hashed_password: str

class UserCreate():
    user_id: int 
    username: str
    password_preprocessed: str
    name: str or None = None
    isOwner: bool
    isAdmin: bool
    disabled: bool or None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto" )
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_all_username(userlist: dict):
    user_arr = []
    for user in userlist:
        user_arr.append(user.lower())
    return user_arr

def get_user(userlist: dict, username: str):
    arr_username = get_all_username(users_data)
    if username.lower() in arr_username:
        user_data = userlist[username]
        return UserInDB(**user_data)
    
def authenticate_user(users_data, username:str, password:str):
    user = get_user(users_data, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    return user





    


    

    

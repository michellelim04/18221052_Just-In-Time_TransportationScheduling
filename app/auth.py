from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import json

SECRET_KEY = "f38a321f31a41f7d61a1b4076f3a196eb261727a8d833e2a841f04f7948fc92d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 10


router = APIRouter(
	prefix="/auth",
	tags=["auth"],
  responses={404: {"description": "Not found"}},
)

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
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl = "/auth/token")

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





async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate":"Bearer"} )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData (username=username)
    except JWTError:
        raise credential_exception
    user = get_user(users_data, username = token_data.username)
    
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    # if current_user.disabled: 
    #     raise HTTPException(status_code = 400, detail="Inactive user")
    
    return current_user

def create_access_token(data:dict, expires_delta: timedelta or None=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = 15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt



@router.post("/token", response_model = Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
	user = authenticate_user(users_data, form_data.username, form_data.password)
	if not user:
		raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Incorrect username or password", headers={"WWW-Authenticate":"Bearer"})
	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
	access_token = create_access_token(data={"sub": user.username}, expires_delta= access_token_expires)
	return {"access_token": access_token, "token_type":"bearer"}





    


    

    

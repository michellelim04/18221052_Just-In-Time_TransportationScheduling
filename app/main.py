from fastapi  import FastAPI

from .routers import driver, schedule, vehicle

from .auth import *

tags_metadata = [
	  {
		  "name" : "driver",
		  "description" : "This route of Driver's Directory allows you to Search, Get, Add, Update, and Delete Drivers' Data."},
	  {
		  "name" : "schedule",
		  "description" : "This route of Transportation Scheduling allows you to Search, Get, Add, Update, and Delete Schedules' Data. The Update feature ensures Just-In-Time Delivery by allowing Transportation Status Updates"},

	  {
		  "name" : "vehicle",
		  "description" : "This route of Vehicle's Directory allows you to Search, Get, Add, Update, and Delete Vehicles' Data."}

  ]

app = FastAPI(openapi_tags=tags_metadata)


app.include_router(driver.app)
app.include_router(schedule.app)
app.include_router(vehicle.app)

def create_access_token(data:dict, expires_delta: timedelta or None=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = 15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

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


@app.post("/token", response_model = Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
	user = authenticate_user(users_data, form_data.username, form_data.password)
	if not user:
		raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Incorrect username or password", headers={"WWW-Authenticate":"Bearer"})
	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
	access_token = create_access_token(data={"sub": user.username}, expires_delta= access_token_expires)
	return {"access_token": access_token, "token_type":"bearer"}

@app.get("/users/me/items", response_model = User)
async def read_own_items(current_user: User = Depends(get_current_active_user)):
	return [{"item_id": 1, "owner": current_user}]



    
# Register a new user
@app.post('/register')
async def register_user(new_user: User, current_user: User = Depends(get_current_active_user)):
    user_dict = new_user.dict()
    user_found = False

    for user in users_data:
        if new_user.username == user or new_user.user_id == user[0]:
            user_found = True
    
    if not user_found:
        createdUser = UserCreate()
        createdUser.user_id = new_user.user_id
        createdUser.username = new_user.username
        createdUser.password_preprocessed = ""
        createdUser.hashed_password = get_password_hash(new_user.password_preprocessed)
        createdUser.isOwner = 0
        createdUser.isAdmin = 1
        createdUser.disabled = 0

        finalNewUser = vars(createdUser)

        users_data[new_user.username]= finalNewUser
        

        with open("./app/json/users.json", "w") as write_file:
            json.dump(users_data, write_file, indent=2)

        return finalNewUser

    else:
        return "Username or ID taken"


@app.get("/")
def read_root():
	return {"message": "Hello World"}

@app.get("/ping")
def ping():
	return {"status": 200, "valid": 1, "message": "pong"}
